'use strict';
/**
 * npm run demo   -- the whole practical in one narrated run, with NO Docker, RabbitMQ or Consul.
 * It uses the in-repo stand-ins (registry/mock-consul.js and lib/fake-amqp.js). The application
 * code it exercises (consul-client, producer, consumer, bridge, function) is the same code that
 * talks to the real services when AMQP_URL / CONSUL_URL point at them.
 */
const { startMockConsul } = require('./registry/mock-consul');
const { registerService, discoverHealthy, deregisterService } = require('./registry/consul-client');
const { startAttendanceService } = require('./services/attendance-service');
const { publishAttendanceMarked } = require('./broker/producer');
const { startConsumer, notifyHandler } = require('./broker/consumer');
const { startBridge } = require('./serverless/bridge');
const { sendAttendanceEmail } = require('./serverless/index');
const { serveFunction } = require('./test-support/helpers');
const { FakeBroker } = require('./lib/fake-amqp');
const { MemoryStore } = require('./broker/idempotency');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const step = (title) => console.log(`\n=== ${title}`);

(async () => {
  const broker = new FakeBroker();
  const amqp = broker.amqp();
  const consul = await startMockConsul({ port: 0 });
  const attendance = await startAttendanceService({ port: 0, publish: (e) => publishAttendanceMarked(e, { amqp }) });
  const fn = await serveFunction(sendAttendanceEmail);

  step('Task 1: register Attendance in the registry and discover it');
  await registerService({ name: 'attendance', id: 'attendance-1', port: attendance.port, interval: '200ms', base: consul.url });
  await sleep(400);
  let found = await discoverHealthy('attendance', { base: consul.url });
  console.log('healthy attendance instances:', found.map((i) => `${i.address}:${i.port}`));

  step('Checkpoint: make /health fail; the instance leaves the passing=true list');
  await fetch(`http://127.0.0.1:${attendance.port}/health/fail`, { method: 'POST' });
  await sleep(600);
  found = await discoverHealthy('attendance', { base: consul.url });
  console.log('healthy attendance instances:', found.map((i) => `${i.address}:${i.port}`), '<- empty: clients stop sending traffic to it');
  await fetch(`http://127.0.0.1:${attendance.port}/health/recover`, { method: 'POST' });
  await sleep(600);
  found = await discoverHealthy('attendance', { base: consul.url });
  console.log('after recovery:', found.map((i) => `${i.address}:${i.port}`));

  step('Task 2: attendance.marked event, idempotent Notification consumer');
  const ch = await (await amqp.connect()).createChannel();
  await startConsumer({ channel: ch, handler: (e) => notifyHandler(e), store: new MemoryStore(), logger: { info: (m) => console.log('  [consumer]', m), error: console.error } });
  const [{ address, port }] = found;
  const post = (body) => fetch(`http://${address}:${port}/attendance`, { method: 'POST', body: JSON.stringify(body) }).then((r) => r.status);
  console.log('POST /attendance eventId=evt-0001 ->', await post({ eventId: 'evt-0001', studentId: 'S102', classId: 'class-5A', present: true }));
  console.log('POST /attendance eventId=evt-0001 again (retry) ->', await post({ eventId: 'evt-0001', studentId: 'S102', classId: 'class-5A', present: true }));
  await broker.drain();
  console.log('=> only ONE "notify:" line above: at-least-once delivery + idempotent consumer');

  step('Task 3: serverless function as a second consumer (bridge -> function)');
  const ch2 = await (await amqp.connect()).createChannel();
  await startBridge({ channel: ch2, functionUrl: fn.url, store: new MemoryStore(), queue: 'sms.email', logger: { info: () => {}, error: console.error } });
  console.log('publishing to the e-mail queue twice with the same eventId...');
  const { publishAttendanceMarked: pub } = require('./broker/producer');
  const ev = { eventId: 'evt-0002', type: 'attendance.marked', classId: 'class-5A', studentId: 'S103', present: false, at: Date.now() };
  await pub(ev, { amqp, queue: 'sms.email' });
  await pub(ev, { amqp, queue: 'sms.email' });
  await broker.drain();
  await sleep(100);
  console.log('(the function logs one dry-run JSON line above: MAIL_API_URL is not set, so nothing is really sent)');

  await deregisterService('attendance-1', { base: consul.url });
  await attendance.close(); await fn.close(); await consul.close();
  console.log('\nbroker stats:', broker.stats);
})().catch((e) => { console.error(e); process.exit(1); });
