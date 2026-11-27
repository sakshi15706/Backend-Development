'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { Recorder, percentile } = require('../lib/metrics');
const { createApp } = require('../app');

async function start(t, opts) {
  const recorder = new Recorder(opts).start();
  const app = createApp({ recorder });
  const server = await new Promise((r) => { const s = app.listen(0, '127.0.0.1', () => r(s)); });
  t.after(() => { recorder.stop(); server.close(); });
  const base = `http://127.0.0.1:${server.address().port}`;
  const get = (p) => fetch(base + p);
  const metrics = async (q = '') => (await get('/metrics' + q)).json();
  return { recorder, base, get, metrics };
}

// ---------------------------------------------------------------- percentile maths
test('percentile uses the nearest-rank rule', () => {
  const v = Array.from({ length: 100 }, (_, i) => i + 1);          // 1..100
  assert.equal(percentile(v, 0.50), 50);
  assert.equal(percentile(v, 0.95), 95);
  assert.equal(percentile(v, 0.99), 99);                           // the slide's floor(n*p) would give 100 here
  assert.equal(percentile(v, 1), 100);
});

test('percentile of small and empty samples', () => {
  assert.equal(percentile([], 0.99), 0);
  assert.equal(percentile([7], 0.5), 7);
  assert.equal(percentile([1, 2], 0.5), 1);
  assert.equal(percentile([1, 2], 0.99), 2);
});

test('the mean hides a bad tail: why you never report only the mean', () => {
  const r = new Recorder();
  for (let i = 0; i < 99; i++) r.record('/x', 10, 200);
  r.record('/x', 800, 200);                                        // 1 request in 100 is very slow
  const s = r.snapshot();
  assert.equal(s.p50, 10);
  assert.equal(s.p95, 10);
  assert.equal(s.max, 800);
  assert.ok(s.mean < 20, `mean ${s.mean} looks healthy`);          // 17.9
  assert.equal(s.p99, 10);                                         // p99 over 100 samples is the 99th value...
  r.record('/x', 800, 200);                                        // ...but with 2 slow of 101 the p99 catches it
  assert.equal(r.snapshot().p99, 800);
});

test('p99 = 120 ms means 1 request in 100 took longer than 120 ms (checkpoint)', () => {
  const r = new Recorder();
  for (let i = 1; i <= 99; i++) r.record('/x', 50, 200);
  r.record('/x', 500, 200);
  r.record('/x', 500, 200);
  assert.ok(r.snapshot().p99 >= 120);
});

// ---------------------------------------------------------------- recorder behaviour
test('window is bounded to windowSize samples but counters keep counting', () => {
  const r = new Recorder({ windowSize: 5 });
  for (let i = 0; i < 12; i++) r.record('/x', i, 200);
  const s = r.snapshot();
  assert.equal(s.count, 5);
  assert.equal(s.totalRequests, 12);
  assert.equal(s.max, 11);                                         // oldest samples were dropped
});

test('error rate counts server errors (5xx) as a percentage of all requests', () => {
  const r = new Recorder();
  for (let i = 0; i < 8; i++) r.record('/x', 1, 200);
  r.record('/x', 1, 404);                                          // client error: not a server error
  r.record('/x', 1, 500);
  const s = r.snapshot();
  assert.equal(s.errors, 1);
  assert.equal(s.errorRate, 10);
});

test('snapshot can be limited to one path', () => {
  const r = new Recorder();
  r.record('/fast', 1, 200); r.record('/slow', 100, 200);
  assert.equal(r.snapshot({ path: '/slow' }).p50, 100);
  assert.equal(r.snapshot({ path: '/fast' }).count, 1);
});

test('reset clears everything', () => {
  const r = new Recorder();
  r.record('/x', 5, 500);
  r.reset();
  const s = r.snapshot();
  assert.deepEqual([s.count, s.totalRequests, s.errors, s.p99], [0, 0, 0, 0]);
});

test('an empty recorder returns zeros, not NaN or a crash', () => {
  const s = new Recorder().snapshot();
  assert.equal(s.count, 0); assert.equal(s.p99, 0); assert.equal(s.mean, 0); assert.equal(s.errorRate, 0);
});

// ---------------------------------------------------------------- the Express app
test('Task 1 checkpoint: /api/ping then /metrics returns count, p50, p95, p99', async (t) => {
  const { get, metrics } = await start(t);
  for (let i = 0; i < 10; i++) await get('/api/ping');
  const m = await metrics();
  assert.equal(m.count, 10);
  for (const k of ['p50', 'p95', 'p99', 'max']) assert.equal(typeof m[k], 'number', k);
  assert.ok(m.p50 > 0 && m.p50 <= m.p95 && m.p95 <= m.p99 && m.p99 <= m.max);
});

test('reading /metrics does not change the metrics', async (t) => {
  const { get, metrics } = await start(t);
  await get('/api/ping');
  await metrics(); await metrics(); await metrics();
  assert.equal((await metrics()).count, 1);
});

test('unknown routes (404) are timed too, and are not counted as server errors', async (t) => {
  const { get, metrics } = await start(t);
  await get('/nope');
  const m = await metrics();
  assert.equal(m.count, 1); assert.equal(m.errors, 0);
});

test('a 500 response is counted in the error rate', async (t) => {
  const { get, metrics } = await start(t);
  await get('/api/ping'); await get('/api/error');
  const m = await metrics();
  assert.equal(m.errors, 1); assert.equal(m.errorRate, 50);
});

test('/metrics?path= filters one endpoint (PBL: profile /api/attendance)', async (t) => {
  const { get, metrics } = await start(t);
  await get('/api/ping'); await get('/api/attendance'); await get('/api/attendance');
  assert.equal((await metrics('?path=/api/attendance')).count, 2);
});

test('POST /metrics/reset starts a clean measurement (use between experiments)', async (t) => {
  const { get, base, metrics } = await start(t);
  await get('/api/ping');
  await fetch(base + '/metrics/reset', { method: 'POST' });
  assert.equal((await metrics()).totalRequests, 0);
});

test('/metrics also reports throughput, memory and event-loop delay', async (t) => {
  const { get, metrics } = await start(t);
  for (let i = 0; i < 5; i++) await get('/api/ping');
  const m = await metrics();
  assert.ok(m.requestsPerSecond > 0);
  assert.ok(m.memory.rssMB > 0 && m.memory.heapUsedMB > 0);
  assert.ok(m.eventLoopDelayMs.p99 >= 0);
  assert.ok(m.cpuSeconds > 0);
});

// ---------------------------------------------------------------- Task 3: bottleneck experiments
test('Task 3: a 50 ms await in the handler raises p50 by about 50 ms', async (t) => {
  const { get, metrics } = await start(t);
  for (let i = 0; i < 20; i++) await get('/api/ping');
  const before = (await metrics()).p50;
  process.env.PING_DELAY_MS = '50';
  t.after(() => { delete process.env.PING_DELAY_MS; });
  const { get: get2, metrics: metrics2 } = await start(t);
  for (let i = 0; i < 20; i++) await get2('/api/ping');
  const after = (await metrics2()).p50;
  assert.ok(after - before >= 40 && after - before <= 120, `p50 went from ${before} to ${after} ms`);
});

test('an async delay does NOT block the event loop (other requests still run)', async (t) => {
  process.env.PING_DELAY_MS = '100';
  t.after(() => { delete process.env.PING_DELAY_MS; });
  const { get, metrics } = await start(t);
  const started = performance.now();
  await Promise.all(Array.from({ length: 20 }, () => get('/api/ping')));       // 20 concurrent x 100 ms
  const elapsed = performance.now() - started;
  assert.ok(elapsed < 1000, `20 concurrent 100 ms requests took ${elapsed} ms (serial would be 2000)`);
  assert.ok((await metrics()).eventLoopDelayMs.p99 < 50);
});

test('a synchronous busy loop DOES block the event loop and shows up as event-loop delay', async (t) => {
  process.env.PING_BLOCK_MS = '60';
  t.after(() => { delete process.env.PING_BLOCK_MS; });
  const { get, metrics } = await start(t, { eventLoopResolution: 10 });
  const started = performance.now();
  await Promise.all(Array.from({ length: 10 }, () => get('/api/ping')));       // 10 x 60 ms, strictly one after another
  const elapsed = performance.now() - started;
  assert.ok(elapsed >= 550, `10 blocking requests took ${elapsed} ms: they could not overlap`);
  const m = await metrics();
  assert.ok(m.eventLoopDelayMs.max >= 30, `event-loop delay max ${m.eventLoopDelayMs.max} ms`);
  // Important: the middleware starts its timer only when Express begins handling a request, so
  // time spent WAITING for the blocked event loop is NOT in the server-side p99 (~60 ms per
  // request). The client (autocannon) sees the queueing; /metrics does not. This is why the
  // slide asks you to compare the two p99 values, and why event-loop delay is tracked as well.
  assert.ok(m.p99 < 100, `server-side p99 ${m.p99} ms does not include queueing`);
});
