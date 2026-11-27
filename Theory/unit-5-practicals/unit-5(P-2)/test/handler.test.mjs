// Task 1-3 and PBL: handler behaviour, with an in-memory DynamoDB (no AWS account needed).
import test from 'node:test';
import assert from 'node:assert/strict';
import { createHandler, HANDLED_TYPES } from '../src/index.mjs';
import { FakeDocClient, sqsRecord, attendanceEvent } from '../test-support/fake-dynamodb.mjs';

const TABLE = 'audit';
const ctx = (remaining = 10000) => ({ awsRequestId: 'req-1', getRemainingTimeInMillis: () => remaining });
const quiet = async (fn) => {                       // keep structured logs out of test output, but let tests read them
  const lines = []; const orig = console.log;
  console.log = (l) => lines.push(JSON.parse(l));
  try { return [await fn(), lines]; } finally { console.log = orig; }
};
const setup = (opts) => { const db = new FakeDocClient(opts); return { db, handler: createHandler({ docClient: db, tableName: TABLE }) }; };
const run = async (handler, records, context = ctx()) => quiet(() => handler({ Records: records }, context));

test('Task 1: one attendance.marked record is written once', async () => {
  const { db, handler } = setup();
  const [result] = await run(handler, [sqsRecord(attendanceEvent())]);
  assert.deepEqual(result, { batchItemFailures: [] });
  const [item] = db.items(TABLE);
  assert.equal(db.items(TABLE).length, 1);
  assert.deepEqual({ ...item, processedAt: undefined }, {
    eventId: 'evt-1001', type: 'attendance.marked', studentId: 'S102', classId: 'class-5A', present: true, at: 1730000000000, processedAt: undefined,
  });
});

test('Task 1 checkpoint: the same event twice leaves exactly one item and no failure', async () => {
  const { db, handler } = setup();
  await run(handler, [sqsRecord(attendanceEvent(), 'm1')]);
  const [second, logs] = await run(handler, [sqsRecord(attendanceEvent(), 'm2')]);
  assert.deepEqual(second, { batchItemFailures: [] });          // a duplicate is a success, not an error
  assert.equal(db.items(TABLE).length, 1);
  assert.ok(logs.some((l) => l.message === 'duplicate event skipped'));
});

test('the write carries the ConditionExpression that makes it idempotent', async () => {
  const { db, handler } = setup();
  await run(handler, [sqsRecord(attendanceEvent())]);
  assert.equal(db.calls[0].ConditionExpression, 'attribute_not_exists(eventId)');
  assert.equal(db.calls[0].TableName, TABLE);
});

test('the first write wins: a duplicate does not overwrite the stored item', async () => {
  const { db, handler } = setup();
  await run(handler, [sqsRecord(attendanceEvent({ present: true }))]);
  await run(handler, [sqsRecord(attendanceEvent({ present: false }))]);
  assert.equal(db.items(TABLE)[0].present, true);
});

test('duplicates inside one batch are handled too', async () => {
  const { db, handler } = setup();
  const [result] = await run(handler, [sqsRecord(attendanceEvent(), 'a'), sqsRecord(attendanceEvent(), 'b')]);
  assert.deepEqual(result.batchItemFailures, []);
  assert.equal(db.items(TABLE).length, 1);
});

test('different eventIds create different items', async () => {
  const { db, handler } = setup();
  await run(handler, [1, 2, 3].map((n) => sqsRecord(attendanceEvent({ eventId: `evt-${n}` }))));
  assert.equal(db.items(TABLE).length, 3);
});

test('result.published (the PBL event) is handled as well', async () => {
  const { db, handler } = setup();
  await run(handler, [sqsRecord({ eventId: 'res-1', type: 'result.published', studentId: 'S9', classId: 'class-5A', at: 5 })]);
  assert.equal(db.items(TABLE)[0].type, 'result.published');
  assert.ok(HANDLED_TYPES.has('attendance.marked') && HANDLED_TYPES.has('result.published'));
});

test('unknown event types are ignored without failing', async () => {
  const { db, handler } = setup();
  const [result] = await run(handler, [sqsRecord({ eventId: 'x', type: 'something.else' })]);
  assert.deepEqual(result, { batchItemFailures: [] });
  assert.equal(db.calls.length, 0);
});

test('partial batch response: only the bad records are reported', async () => {
  const { db, handler } = setup();
  const [result] = await run(handler, [
    sqsRecord(attendanceEvent({ eventId: 'ok-1' }), 'good-1'),
    sqsRecord('this is not json', 'bad-json'),
    sqsRecord({ type: 'attendance.marked', studentId: 'S1' }, 'no-id'),
    sqsRecord(attendanceEvent({ eventId: 'ok-2' }), 'good-2'),
  ]);
  assert.deepEqual(result.batchItemFailures, [{ itemIdentifier: 'bad-json' }, { itemIdentifier: 'no-id' }]);
  assert.equal(db.items(TABLE).length, 2);                      // the good ones were still stored
});

test('a throttled write fails only that record, so SQS retries it', async () => {
  const { db, handler } = setup({ failFor: new Set(['evt-b']) });
  const [result] = await run(handler, [
    sqsRecord(attendanceEvent({ eventId: 'evt-a' }), 'ma'),
    sqsRecord(attendanceEvent({ eventId: 'evt-b' }), 'mb'),
    sqsRecord(attendanceEvent({ eventId: 'evt-c' }), 'mc'),
  ]);
  assert.deepEqual(result.batchItemFailures, [{ itemIdentifier: 'mb' }]);
  assert.deepEqual(db.items(TABLE).map((i) => i.eventId).sort(), ['evt-a', 'evt-c']);
});

test('Task 2 checkpoint: without dynamodb:PutItem every record fails with AccessDenied (least privilege works)', async () => {
  const { db, handler } = setup({ deny: true });
  const [result, logs] = await run(handler, [sqsRecord(attendanceEvent({ eventId: 'e1' }), 'm1'), sqsRecord(attendanceEvent({ eventId: 'e2' }), 'm2')]);
  assert.deepEqual(result.batchItemFailures, [{ itemIdentifier: 'm1' }, { itemIdentifier: 'm2' }]);
  assert.equal(db.items(TABLE).length, 0);
  assert.ok(logs.some((l) => l.level === 'ERROR' && l.error === 'AccessDeniedException'));
});

test('a retry after a failure succeeds and is still stored exactly once', async () => {
  const failing = new Set(['evt-1']);
  const db = new FakeDocClient({ failFor: failing });
  const handler = createHandler({ docClient: db, tableName: TABLE });
  const [first] = await run(handler, [sqsRecord(attendanceEvent({ eventId: 'evt-1' }), 'm1')]);
  assert.equal(first.batchItemFailures.length, 1);
  failing.clear();                                              // the throttling is over; SQS redelivers
  const [second] = await run(handler, [sqsRecord(attendanceEvent({ eventId: 'evt-1' }), 'm1')]);
  assert.deepEqual(second.batchItemFailures, []);
  assert.equal(db.items(TABLE).length, 1);
});

test('running out of time returns the remaining records for retry instead of cutting them off', async () => {
  const { db, handler } = setup();
  let remaining = 5000;
  const context = { awsRequestId: 'r', getRemainingTimeInMillis: () => { const v = remaining; remaining -= 4500; return v; } };
  const [result] = await run(handler, [
    sqsRecord(attendanceEvent({ eventId: 'e1' }), 'm1'),
    sqsRecord(attendanceEvent({ eventId: 'e2' }), 'm2'),
    sqsRecord(attendanceEvent({ eventId: 'e3' }), 'm3'),
  ], context);
  assert.deepEqual(result.batchItemFailures, [{ itemIdentifier: 'm2' }, { itemIdentifier: 'm3' }]);
  assert.equal(db.items(TABLE).length, 1);
});

test('an empty or missing Records list is fine', async () => {
  const { handler } = setup();
  assert.deepEqual((await quiet(() => handler({ Records: [] }, ctx())))[0], { batchItemFailures: [] });
  assert.deepEqual((await quiet(() => handler({}, ctx())))[0], { batchItemFailures: [] });
});

test('the handler refuses to run without AUDIT_TABLE', async () => {
  const saved = process.env.AUDIT_TABLE; delete process.env.AUDIT_TABLE;
  try {
    const handler = createHandler({ docClient: new FakeDocClient() });
    await assert.rejects(() => handler({ Records: [] }, ctx()), /AUDIT_TABLE is not set/);
  } finally { if (saved !== undefined) process.env.AUDIT_TABLE = saved; }
});

test('table name comes from the environment (as in template.yaml)', async () => {
  process.env.AUDIT_TABLE = 'env-table';
  try {
    const db = new FakeDocClient();
    await run(createHandler({ docClient: db }), [sqsRecord(attendanceEvent())]);
    assert.equal(db.items('env-table').length, 1);
  } finally { delete process.env.AUDIT_TABLE; }
});

test('statelessness: results do not depend on earlier invocations of the same handler', async () => {
  const { handler } = setup();
  const a = await run(handler, [sqsRecord('not json', 'x')]);
  const b = await run(handler, [sqsRecord('not json', 'x')]);
  assert.deepEqual(a[0], b[0]);
});

test('no secrets or credentials appear in the source', async () => {
  const { readFileSync } = await import('node:fs');
  const src = readFileSync(new URL('../src/index.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(src, /AKIA[0-9A-Z]{16}|aws_secret_access_key|secretAccessKey/i);
});

test('the exported handler is a function with the (event, context) contract', async () => {
  const { handler } = await import('../src/index.mjs');
  assert.equal(typeof handler, 'function');
  assert.equal(handler.length, 2);
});
