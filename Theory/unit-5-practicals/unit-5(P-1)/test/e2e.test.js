'use strict';
// PBL "Integrate": registry + broker + idempotent consumer + serverless function, end to end.
const test = require('node:test');
const assert = require('node:assert/strict');
const { startMockConsul } = require('../registry/mock-consul');
const { registerService, discoverHealthy, roundRobin } = require('../registry/consul-client');
const { startAttendanceService } = require('../services/attendance-service');
const { publishAttendanceMarked } = require('../broker/producer');
const { startConsumer, notifyHandler } = require('../broker/consumer');
const { startBridge } = require('../serverless/bridge');
const { sendAttendanceEmail } = require('../serverless/index');
const { FakeBroker } = require('../lib/fake-amqp');
const { MemoryStore } = require('../broker/idempotency');
const { serveFunction, waitFor, silent } = require('../test-support/helpers');

async function system(t) {
  const broker = new FakeBroker();
  const amqp = broker.amqp();
  const consul = await startMockConsul({ port: 0 });
  const attendance = await startAttendanceService({ port: 0, publish: (e) => publishAttendanceMarked(e, { amqp }) });

  // Notification service: two independent consumers of the event (each needs its own queue in real
  // RabbitMQ via an exchange; here we use two queues fed by the same producer helper for clarity).
  const notifications = [];
  const channel = await (await amqp.connect()).createChannel();
  await startConsumer({ channel, handler: async (e) => notifyHandler(e, { log: (...a) => notifications.push(a.join(' ')) }), store: new MemoryStore(), logger: silent });

  t.after(async () => { await attendance.close(); await consul.close(); });
  await registerService({ name: 'attendance', id: 'attendance-1', port: attendance.port, interval: '100ms', base: consul.url });
  const [instance] = await waitFor(async () => { const l = await discoverHealthy('attendance', { base: consul.url }); return l.length ? l : null; });
  const post = (body) => fetch(`http://${instance.address}:${instance.port}/attendance`, { method: 'POST', body: JSON.stringify(body) });
  return { broker, consul, notifications, post, instance };
}

test('client finds Attendance through the registry, marks attendance, Notification gets the event', async (t) => {
  const { broker, notifications, post } = await system(t);
  const res = await post({ studentId: 'S102', classId: 'class-5A', present: true });
  assert.equal(res.status, 202);
  const { eventId } = await res.json();
  assert.match(eventId, /^[0-9a-f-]{36}$/);
  await broker.drain();
  assert.deepEqual(notifications, ['notify: S102 was present']);
});

test('PBL duplicate-event test: a retried request with the same eventId notifies once', async (t) => {
  const { broker, notifications, post } = await system(t);
  await post({ eventId: 'evt-dup', studentId: 'S102', classId: 'class-5A', present: false });
  await post({ eventId: 'evt-dup', studentId: 'S102', classId: 'class-5A', present: false });
  await broker.drain();
  assert.deepEqual(notifications, ['notify: S102 was absent']);
});

test('the producer is decoupled: attendance still answers 202 while nobody consumes', async (t) => {
  const broker = new FakeBroker();
  const attendance = await startAttendanceService({ port: 0, publish: (e) => publishAttendanceMarked(e, { amqp: broker.amqp() }) });
  t.after(() => attendance.close());
  const res = await fetch(`http://127.0.0.1:${attendance.port}/attendance`, { method: 'POST', body: JSON.stringify({ studentId: 'S1', classId: 'c', present: true }) });
  assert.equal(res.status, 202);
  assert.equal(broker.queue('sms.events').ready.length, 1);   // buffered until a consumer shows up
});

test('Attendance answers 503 if the broker is unreachable', async (t) => {
  const attendance = await startAttendanceService({ port: 0, publish: async () => { throw new Error('ECONNREFUSED'); } });
  t.after(() => attendance.close());
  const res = await fetch(`http://127.0.0.1:${attendance.port}/attendance`, { method: 'POST', body: JSON.stringify({ studentId: 'S1', classId: 'c', present: true }) });
  assert.equal(res.status, 503);
});

test('Attendance validates its input', async (t) => {
  const attendance = await startAttendanceService({ port: 0, publish: async () => {} });
  t.after(() => attendance.close());
  const url = `http://127.0.0.1:${attendance.port}/attendance`;
  assert.equal((await fetch(url, { method: 'POST', body: '{bad' })).status, 400);
  assert.equal((await fetch(url, { method: 'POST', body: JSON.stringify({ studentId: 'S1' }) })).status, 400);
  assert.equal((await fetch(url, { method: 'POST', body: JSON.stringify({ studentId: 'S1', classId: 'c', present: 'yes' }) })).status, 400);
  assert.equal((await fetch(`http://127.0.0.1:${attendance.port}/nothing`)).status, 404);
});

test('the full chain: registry -> attendance -> broker -> bridge -> serverless function (sent once)', async (t) => {
  const broker = new FakeBroker();
  const amqp = broker.amqp();
  const attendance = await startAttendanceService({ port: 0, publish: (e) => publishAttendanceMarked(e, { amqp }) });
  const emails = [];
  const fn = await serveFunction((req, res) => { emails.push(req.body.eventId); return sendAttendanceEmail(req, res); });
  t.after(async () => { await attendance.close(); await fn.close(); });
  const channel = await (await amqp.connect()).createChannel();
  await startBridge({ channel, functionUrl: fn.url, store: new MemoryStore(), logger: silent });

  for (let i = 0; i < 2; i++) {
    await fetch(`http://127.0.0.1:${attendance.port}/attendance`, { method: 'POST', body: JSON.stringify({ eventId: 'evt-9', studentId: 'S7', classId: 'c', present: true }) });
  }
  await broker.drain();
  assert.deepEqual(emails, ['evt-9']);
});
