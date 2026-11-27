'use strict';
// Task 2: attendance.marked over a queue, with an idempotent consumer.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { FakeBroker } = require('../lib/fake-amqp');
const { publishAttendanceMarked, validateEvent } = require('../broker/producer');
const { startConsumer, notifyHandler } = require('../broker/consumer');
const { MemoryStore, FileStore } = require('../broker/idempotency');
const { silent, sample } = require('../test-support/helpers');

async function setup({ handler, store = new MemoryStore(), prefetch = 10 } = {}) {
  const broker = new FakeBroker();
  const amqp = broker.amqp();
  const channel = await (await amqp.connect()).createChannel();
  const handled = [];
  await startConsumer({ channel, store, prefetch, logger: silent, handler: handler || (async (e) => { handled.push(e.eventId); }) });
  const publish = (event) => publishAttendanceMarked(event, { amqp });
  return { broker, amqp, channel, handled, publish, store };
}

test('one event produces exactly one notification line', async () => {
  const lines = [];
  const { broker, publish } = await setup({ handler: async (e) => notifyHandler(e, { log: (...a) => lines.push(a.join(' ')) }) });
  await publish(sample());
  await broker.drain();
  assert.deepEqual(lines, ['notify: S102 was present']);
});

test('absent students are reported as absent', async () => {
  const lines = [];
  const { broker, publish } = await setup({ handler: async (e) => notifyHandler(e, { log: (...a) => lines.push(a.join(' ')) }) });
  await publish(sample({ present: false }));
  await broker.drain();
  assert.deepEqual(lines, ['notify: S102 was absent']);
});

test('Task 2 checkpoint: the same eventId published twice is processed once', async () => {
  const { broker, publish, handled } = await setup();
  await publish(sample());
  await publish(sample());
  await broker.drain();
  assert.deepEqual(handled, ['evt-0001']);
  assert.equal(broker.stats.published, 2);
  assert.equal(broker.stats.acked, 2);               // the duplicate is acknowledged (and skipped), not left in the queue
});

test('different eventIds are all processed', async () => {
  const { broker, publish, handled } = await setup();
  for (const id of ['a', 'b', 'c']) await publish(sample({ eventId: id }));
  await broker.drain();
  assert.deepEqual(handled.sort(), ['a', 'b', 'c']);
});

test('duplicates arriving at the same moment (prefetch > 1) are still processed once', async () => {
  let calls = 0;
  const { broker, publish } = await setup({
    prefetch: 10,
    handler: async () => { calls += 1; await new Promise((r) => setTimeout(r, 30)); },   // slow handler: both copies are in flight
  });
  await publish(sample());
  await publish(sample());
  await publish(sample());
  await broker.drain();
  assert.equal(calls, 1);
});

test('a failing handler is retried (nack + requeue) and the event is processed once it succeeds', async () => {
  let attempts = 0;
  const done = [];
  const { broker, publish } = await setup({
    handler: async (e) => { attempts += 1; if (attempts < 3) throw new Error('mail server down'); done.push(e.eventId); },
  });
  await publish(sample());
  await broker.drain();
  assert.equal(attempts, 3);
  assert.deepEqual(done, ['evt-0001']);
  assert.equal(broker.stats.redelivered, 2);
});

test('why the id is stored AFTER success: the slide order loses an event when the handler fails', async () => {
  // slide version: seen.add(id) first, then process. If processing throws, the redelivery is dropped as a "duplicate".
  const broker = new FakeBroker();
  const channel = await (await broker.amqp().connect()).createChannel();
  await channel.assertQueue('sms.events');
  const seen = new Set(); const processed = []; let first = true;
  await channel.consume('sms.events', async (msg) => {
    const event = JSON.parse(msg.content.toString());
    if (seen.has(event.eventId)) return channel.ack(msg);
    seen.add(event.eventId);                                  // too early
    if (first) { first = false; return channel.nack(msg, false, true); }   // simulated crash after marking
    processed.push(event.eventId); channel.ack(msg);
  });
  channel.sendToQueue('sms.events', Buffer.from(JSON.stringify(sample())));
  await broker.drain();
  assert.deepEqual(processed, []);                            // the notification was LOST
});

test('a failed event is not remembered as processed', async () => {
  const store = new MemoryStore();
  let fail = true;
  const { broker, publish } = await setup({ store, handler: async () => { if (fail) { fail = false; throw new Error('x'); } } });
  await publish(sample());
  await broker.drain();
  assert.equal(await store.has('evt-0001'), true);            // remembered only after the second (successful) attempt
});

test('invalid JSON is rejected without requeue (no endless loop)', async () => {
  const { broker, channel, handled } = await setup();
  channel.sendToQueue('sms.events', Buffer.from('{not json'));
  await broker.drain();
  assert.equal(broker.stats.nacked, 1);
  assert.equal(broker.stats.redelivered, 0);
  assert.deepEqual(handled, []);
});

test('a message without eventId is rejected without requeue', async () => {
  const { broker, channel, handled } = await setup();
  channel.sendToQueue('sms.events', Buffer.from(JSON.stringify({ type: 'attendance.marked' })));
  await broker.drain();
  assert.equal(broker.stats.redelivered, 0);
  assert.deepEqual(handled, []);
});

test('an unacknowledged message is redelivered when the consumer disconnects', async () => {
  const broker = new FakeBroker();
  const amqp = broker.amqp();
  const first = await (await amqp.connect()).createChannel();
  await first.assertQueue('sms.events');
  await first.consume('sms.events', () => { /* crashes before ack */ });
  first.sendToQueue('sms.events', Buffer.from(JSON.stringify(sample())));
  await broker.drain(50).catch(() => {});                     // in flight, never acked
  await first.close();                                        // consumer dies

  const second = await (await amqp.connect()).createChannel();
  const got = [];
  await second.consume('sms.events', (msg) => { got.push(msg.fields.redelivered); second.ack(msg); });
  await broker.drain();
  assert.deepEqual(got, [true]);                              // at-least-once: it comes back, flagged as redelivered
});

test('FileStore keeps processed ids across a restart', async () => {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'sms-')), 'seen.txt');
  const one = new FileStore(file);
  await one.add('evt-1'); await one.add('evt-1');
  const two = new FileStore(file);                            // "restart"
  assert.equal(await two.has('evt-1'), true);
  assert.equal(await two.has('evt-2'), false);
  assert.equal(fs.readFileSync(file, 'utf8'), 'evt-1\n');     // no duplicate line
});

test('producer validates events before publishing', async () => {
  assert.throws(() => validateEvent({ type: 'attendance.marked' }), /eventId, studentId/);
  assert.throws(() => validateEvent(sample({ type: 'result.published' })), /unsupported event type/);
  await assert.rejects(publishAttendanceMarked({}, { amqp: new FakeBroker().amqp() }), /missing/);
});

test('producer marks queue durable and message persistent (the slide settings)', async () => {
  const calls = {};
  const amqp = { connect: async () => ({
    createChannel: async () => ({
      assertQueue: async (q, o) => { calls.assert = [q, o]; },
      sendToQueue: (q, buf, o) => { calls.send = [q, o]; },
      close: async () => {},
    }),
    close: async () => {},
  }) };
  await publishAttendanceMarked(sample(), { amqp });
  assert.deepEqual(calls.assert, ['sms.events', { durable: true }]);
  assert.deepEqual(calls.send, ['sms.events', { persistent: true }]);
});

test('the producer closes the connection even when publishing fails', async () => {
  let closed = false;
  const amqp = { connect: async () => ({
    createChannel: async () => { throw new Error('channel error'); },
    close: async () => { closed = true; },
  }) };
  await assert.rejects(publishAttendanceMarked(sample(), { amqp }), /channel error/);
  assert.equal(closed, true);
});

test('fan-out note: a second consumer needs its own queue (a work queue delivers each message once)', async () => {
  const broker = new FakeBroker();
  const channel = await (await broker.amqp().connect()).createChannel();
  const a = []; const b = [];
  await channel.assertQueue('q');
  await channel.consume('q', (m) => { a.push(1); channel.ack(m); });
  await channel.consume('q', (m) => { b.push(1); channel.ack(m); });
  for (let i = 0; i < 4; i++) channel.sendToQueue('q', Buffer.from('x'));
  await broker.drain();
  assert.equal(a.length + b.length, 4);                       // shared, not copied: pub/sub needs an exchange
});
