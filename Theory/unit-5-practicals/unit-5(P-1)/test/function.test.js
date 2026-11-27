'use strict';
// Task 3: the serverless function and the bridge that feeds it.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const { sendAttendanceEmail } = require('../serverless/index');
const { startBridge } = require('../serverless/bridge');
const { FakeBroker } = require('../lib/fake-amqp');
const { MemoryStore } = require('../broker/idempotency');
const { serveFunction, silent, sample } = require('../test-support/helpers');

function fakeRes() {
  const res = { statusCode: 200, body: undefined, ended: false };
  res.status = (c) => { res.statusCode = c; return res; };
  res.json = (b) => { res.body = b; res.ended = true; return res; };
  res.end = () => { res.ended = true; return res; };
  return res;
}
const call = async (body) => { const res = fakeRes(); await sendAttendanceEmail({ body }, res); return res; };

test('other event types are ignored with 204', async () => {
  assert.equal((await call({ type: 'result.published', eventId: 'x' })).statusCode, 204);
});

test('a missing body is ignored, not a crash', async () => {
  assert.equal((await call(undefined)).statusCode, 204);
});

test('attendance.marked without studentId or eventId is a 400', async () => {
  assert.equal((await call(sample({ studentId: undefined }))).statusCode, 400);
  assert.equal((await call(sample({ eventId: undefined }))).statusCode, 400);
});

test('dry run (no MAIL_API_URL): 200 and nothing is sent', async () => {
  delete process.env.MAIL_API_URL;
  const res = await call(sample());
  assert.equal(res.statusCode, 200);
  assert.deepEqual(res.body, { ok: true, dryRun: true, eventId: 'evt-0001' });
});

test('with MAIL_API_URL the function posts the e-mail and answers 200', async (t) => {
  const sent = [];
  const mail = await serveFunction((req, res) => { sent.push(req.body); res.status(200).json({ queued: true }); });
  t.after(() => mail.close());
  process.env.MAIL_API_URL = mail.url;
  t.after(() => { delete process.env.MAIL_API_URL; });
  const res = await call(sample());
  assert.equal(res.statusCode, 200);
  assert.deepEqual(sent[0].to, 'S102@sms.example');
  assert.equal(sent[0].subject, 'Attendance update');
  assert.match(sent[0].text, /present/);
});

test('a failing mail provider gives 502 so the caller retries', async (t) => {
  const mail = await serveFunction((req, res) => res.status(500).json({}));
  t.after(() => mail.close());
  process.env.MAIL_API_URL = mail.url;
  t.after(() => { delete process.env.MAIL_API_URL; });
  const res = await call(sample());
  assert.equal(res.statusCode, 502);
  assert.deepEqual(res.body, { ok: false, error: 'mail provider unavailable' });
});

test('an unreachable mail provider gives 502, not an unhandled error', async (t) => {
  process.env.MAIL_API_URL = 'http://127.0.0.1:1/send';
  t.after(() => { delete process.env.MAIL_API_URL; });
  assert.equal((await call(sample())).statusCode, 502);
});

test('statelessness: the module keeps no data between invocations and opens no connections', () => {
  const source = fs.readFileSync(path.join(__dirname, '../serverless/index.js'), 'utf8');
  assert.equal(/require\(['"](amqplib|ws|socket\.io|pg|mysql2?|mongoose|redis)['"]\)/.test(source), false);
  assert.equal(/^(let|var)\s/m.test(source), false);          // no module-level mutable state
  assert.deepEqual(Object.keys(require('../serverless/index')), ['sendAttendanceEmail']);
});

test('the same input gives the same answer on every call', async () => {
  const a = await call(sample()); const b = await call(sample());
  assert.deepEqual(a.body, b.body);
});

// ---- bridge: broker -> function --------------------------------------------------------------
async function bridgeSetup(t, fn) {
  const broker = new FakeBroker();
  const amqp = broker.amqp();
  const channel = await (await amqp.connect()).createChannel();
  const server = await serveFunction(fn);
  t.after(() => server.close());
  await startBridge({ channel, functionUrl: server.url, store: new MemoryStore(), logger: silent });
  const publish = (e) => channel.sendToQueue('sms.events', Buffer.from(JSON.stringify(e)));
  return { broker, publish, server };
}

test('bridge forwards events to the function over HTTP', async (t) => {
  const got = [];
  const { broker, publish } = await bridgeSetup(t, (req, res) => { got.push(req.body); res.status(200).json({ ok: true }); });
  publish(sample());
  await broker.drain();
  assert.equal(got.length, 1);
  assert.equal(got[0].eventId, 'evt-0001');
});

test('bridge: the same event twice reaches the function once', async (t) => {
  let calls = 0;
  const { broker, publish } = await bridgeSetup(t, (req, res) => { calls += 1; res.status(200).json({ ok: true }); });
  publish(sample()); publish(sample());
  await broker.drain();
  assert.equal(calls, 1);
});

test('bridge: a function error (5xx) makes the broker redeliver until it succeeds', async (t) => {
  let calls = 0;
  const { broker, publish } = await bridgeSetup(t, (req, res) => { calls += 1; res.status(calls < 3 ? 502 : 200).json({}); });
  publish(sample());
  await broker.drain();
  assert.equal(calls, 3);
  assert.equal(broker.stats.redelivered, 2);
});
