/**
 * Lambda handler: SQS -> DynamoDB audit table with an idempotency guard (Lectures 55-57).
 *
 * Differences from the slide's handler, and why:
 *  1. DUPLICATES ARE SKIPPED, not fatal. The slide's PutItem uses
 *     ConditionExpression 'attribute_not_exists(eventId)', but a duplicate makes DynamoDB throw
 *     ConditionalCheckFailedException; uncaught, the whole batch fails and returns to the queue
 *     (and eventually the DLQ) forever. Here that exception means "already processed" = success.
 *  2. PARTIAL BATCH RESPONSE. The handler returns { batchItemFailures: [{ itemIdentifier }] }
 *     for only the records that failed, so one bad record does not re-run the whole batch.
 *     The event source mapping must enable ReportBatchItemFailures (see template.yaml).
 *  3. Other errors (e.g. AccessDeniedException, throttling) fail ONLY that record, so SQS
 *     retries it and finally moves it to the dead-letter queue.
 *  4. Poison messages (invalid JSON, missing eventId) are failed too, so they end in the DLQ for
 *     a human to inspect instead of being silently dropped.
 *  5. Time check: if little time is left before the function timeout, the remaining records are
 *     returned as failures (they are retried) instead of being cut off half-way.
 *  6. The table name comes from an environment variable and the handler refuses to run without it.
 */
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';

export const HANDLED_TYPES = new Set(['attendance.marked', 'result.published']);
const MIN_REMAINING_MS = 1000;

// Created ONCE per execution environment and reused on warm invocations. It is a client object,
// not request state: nothing about one event is remembered between invocations.
let defaultClient;
const getDefaultClient = () => (defaultClient ??= DynamoDBDocumentClient.from(new DynamoDBClient()));

const log = (level, message, extra = {}) =>
  console.log(JSON.stringify({ level, message, ...extra }));      // structured logs for CloudWatch

export function createHandler({ docClient, tableName } = {}) {
  return async (event, context) => {
    context = context ?? {};
    const table = tableName ?? process.env.AUDIT_TABLE;
    if (!table) throw new Error('AUDIT_TABLE is not set');       // configuration error: fail loudly
    const client = docClient ?? getDefaultClient();

    const records = event?.Records ?? [];
    const batchItemFailures = [];
    let processed = 0;
    let duplicates = 0;
    let skipped = 0;

    for (let i = 0; i < records.length; i++) {
      const record = records[i];

      if (typeof context.getRemainingTimeInMillis === 'function' && context.getRemainingTimeInMillis() < MIN_REMAINING_MS) {
        for (const rest of records.slice(i)) batchItemFailures.push({ itemIdentifier: rest.messageId });
        log('WARN', 'out of time, returning unprocessed records for retry', { count: records.length - i, requestId: context.awsRequestId });
        break;
      }

      let payload;
      try {
        payload = JSON.parse(record.body);
      } catch {
        log('ERROR', 'invalid JSON body', { messageId: record.messageId });
        batchItemFailures.push({ itemIdentifier: record.messageId });
        continue;
      }
      if (!payload || typeof payload !== 'object' || !payload.eventId) {
        log('ERROR', 'message has no eventId', { messageId: record.messageId });
        batchItemFailures.push({ itemIdentifier: record.messageId });
        continue;
      }
      if (!HANDLED_TYPES.has(payload.type)) {
        skipped++;
        log('INFO', 'ignoring event type', { type: payload.type, eventId: payload.eventId });
        continue;                                                 // not an error: nothing to do
      }

      try {
        await client.send(new PutCommand({
          TableName: table,
          Item: {
            eventId: payload.eventId,                             // partition key = idempotency key
            type: payload.type,
            studentId: payload.studentId,
            classId: payload.classId,
            present: payload.present,
            at: payload.at,
            processedAt: Date.now(),
          },
          ConditionExpression: 'attribute_not_exists(eventId)',   // only the FIRST write wins
        }));
        processed++;
      } catch (err) {
        if (err.name === 'ConditionalCheckFailedException') {
          duplicates++;                                           // already stored: success, skip
          log('INFO', 'duplicate event skipped', { eventId: payload.eventId });
        } else {
          log('ERROR', 'write failed', { eventId: payload.eventId, error: err.name, detail: err.message });
          batchItemFailures.push({ itemIdentifier: record.messageId });
        }
      }
    }

    log('INFO', 'batch finished', { received: records.length, processed, duplicates, skipped, failed: batchItemFailures.length, requestId: context.awsRequestId });
    return { batchItemFailures };
  };
}

// The function AWS runs: handler setting "index.handler" in the console, Handler: index.handler in SAM
// (SAM builds src/ into the package root).
export const handler = createHandler();
