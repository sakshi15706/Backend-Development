/** In-memory stand-in for DynamoDBDocumentClient.send(PutCommand). Used by tests and invoke-local. */
export class ConditionalCheckFailedException extends Error {
  constructor() { super('The conditional request failed'); this.name = 'ConditionalCheckFailedException'; }
}

export class FakeDocClient {
  constructor({ deny = false, failFor = new Set(), delayMs = 0 } = {}) {
    this.tables = new Map();       // table -> Map(eventId -> item)
    this.calls = [];
    this.deny = deny;              // simulates a role without dynamodb:PutItem
    this.failFor = failFor;        // eventIds that fail with a throttling error
    this.delayMs = delayMs;
  }
  items(table) { return [...(this.tables.get(table)?.values() ?? [])]; }

  async send(command) {
    const input = command.input;
    this.calls.push(input);
    if (this.delayMs) await new Promise((r) => setTimeout(r, this.delayMs));
    if (this.deny) {
      const err = new Error('User is not authorized to perform: dynamodb:PutItem on resource');
      err.name = 'AccessDeniedException';
      throw err;
    }
    if (this.failFor.has(input.Item.eventId)) {
      const err = new Error('Rate exceeded'); err.name = 'ProvisionedThroughputExceededException'; throw err;
    }
    const table = this.tables.get(input.TableName) ?? this.tables.set(input.TableName, new Map()).get(input.TableName);
    // only the condition used in this practical is supported
    if (input.ConditionExpression === 'attribute_not_exists(eventId)' && table.has(input.Item.eventId)) {
      throw new ConditionalCheckFailedException();
    }
    table.set(input.Item.eventId, structuredClone(input.Item));
    return {};
  }
}

export const sqsRecord = (body, messageId = 'm-' + Math.random().toString(36).slice(2, 8)) => ({
  messageId,
  receiptHandle: 'rh-' + messageId,
  body: typeof body === 'string' ? body : JSON.stringify(body),
  attributes: { ApproximateReceiveCount: '1' },
  eventSource: 'aws:sqs',
});

export const attendanceEvent = (over = {}) => ({
  eventId: 'evt-1001', type: 'attendance.marked', studentId: 'S102', classId: 'class-5A', present: true, at: 1730000000000, ...over,
});
