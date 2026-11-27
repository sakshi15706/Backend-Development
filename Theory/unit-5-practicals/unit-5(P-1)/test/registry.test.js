'use strict';
// Task 1: register the Attendance service and discover only healthy instances.
const test = require('node:test');
const assert = require('node:assert/strict');
const { startMockConsul, parseDuration } = require('../registry/mock-consul');
const { registerService, deregisterService, discoverHealthy, roundRobin } = require('../registry/consul-client');
const { startAttendanceService } = require('../services/attendance-service');
const { waitFor } = require('../test-support/helpers');

async function setup(t) {
  const consul = await startMockConsul({ port: 0 });
  const svc = await startAttendanceService({ port: 0, publish: async () => {} });
  t.after(async () => { await svc.close(); await consul.close(); });
  return { consul, svc, base: consul.url };
}
const reg = (base, svc, id = 'attendance-1') =>
  registerService({ name: 'attendance', id, port: svc.port, interval: '100ms', timeout: '500ms', base });

test('a registered instance becomes discoverable once its health check passes', async (t) => {
  const { base, svc } = await setup(t);
  await reg(base, svc);
  const found = await waitFor(async () => { const l = await discoverHealthy('attendance', { base }); return l.length ? l : null; });
  assert.deepEqual(found, [{ id: 'attendance-1', address: '127.0.0.1', port: svc.port }]);
});

test('Task 1 checkpoint: a failing /health removes the instance from the passing=true list', async (t) => {
  const { base, svc } = await setup(t);
  await reg(base, svc);
  await waitFor(async () => (await discoverHealthy('attendance', { base })).length === 1);

  await fetch(`http://127.0.0.1:${svc.port}/health/fail`, { method: 'POST' });
  assert.equal(svc.isFailing(), true);
  await waitFor(async () => (await discoverHealthy('attendance', { base })).length === 0);   // gone, nobody edited the client

  await fetch(`http://127.0.0.1:${svc.port}/health/recover`, { method: 'POST' });             // and it comes back
  await waitFor(async () => (await discoverHealthy('attendance', { base })).length === 1);
});

test('without ?passing=true the unhealthy instance is still listed, marked critical', async (t) => {
  const { base, svc } = await setup(t);
  await reg(base, svc);
  await fetch(`http://127.0.0.1:${svc.port}/health/fail`, { method: 'POST' });
  const rows = await waitFor(async () => {
    const r = await (await fetch(`${base}/v1/health/service/attendance`)).json();
    return r.length && r[0].Checks[0].Status === 'critical' ? r : null;
  });
  assert.equal(rows[0].Service.Port, svc.port);
});

test('an instance that is not running never becomes healthy', async (t) => {
  const consul = await startMockConsul({ port: 0 });
  t.after(() => consul.close());
  await registerService({ name: 'attendance', id: 'ghost', port: 1, interval: '100ms', timeout: '200ms', base: consul.url });
  await new Promise((r) => setTimeout(r, 400));
  assert.deepEqual(await discoverHealthy('attendance', { base: consul.url }), []);
});

test('deregistering on shutdown removes the instance immediately', async (t) => {
  const { base, svc } = await setup(t);
  await reg(base, svc);
  await waitFor(async () => (await discoverHealthy('attendance', { base })).length === 1);
  await deregisterService('attendance-1', { base });
  assert.deepEqual(await discoverHealthy('attendance', { base }), []);
});

test('deregistering an unknown id is an error', async (t) => {
  const { base } = await setup(t);
  await assert.rejects(deregisterService('nope', { base }), /404/);
});

test('registration without a Name is rejected', async (t) => {
  const { base } = await setup(t);
  const res = await fetch(`${base}/v1/agent/service/register`, { method: 'PUT', body: '{"Port": 1}' });
  assert.equal(res.status, 400);
});

test('several healthy replicas: client-side round-robin spreads calls', async (t) => {
  const consul = await startMockConsul({ port: 0 });
  const a = await startAttendanceService({ port: 0, publish: async () => {} });
  const b = await startAttendanceService({ port: 0, publish: async () => {} });
  t.after(async () => { await a.close(); await b.close(); await consul.close(); });
  await registerService({ name: 'attendance', id: 'attendance-a', port: a.port, interval: '100ms', base: consul.url });
  await registerService({ name: 'attendance', id: 'attendance-b', port: b.port, interval: '100ms', base: consul.url });
  await waitFor(async () => (await discoverHealthy('attendance', { base: consul.url })).length === 2);

  const pick = roundRobin();
  const instances = await discoverHealthy('attendance', { base: consul.url });
  const ports = [pick(instances).port, pick(instances).port, pick(instances).port, pick(instances).port];
  assert.equal(new Set(ports).size, 2);                       // both replicas used
  assert.equal(ports[0], ports[2]);                           // strict alternation
});

test('round-robin with no healthy instances fails loudly', () => {
  assert.throws(() => roundRobin()([]), /no healthy instances/);
});

test('a discovered address can really be called', async (t) => {
  const { base, svc } = await setup(t);
  await reg(base, svc);
  const [inst] = await waitFor(async () => { const l = await discoverHealthy('attendance', { base }); return l.length ? l : null; });
  const res = await fetch(`http://${inst.address}:${inst.port}/health`);
  assert.deepEqual(await res.json(), { status: 'UP' });
});

test('duration parser understands Consul-style values', () => {
  assert.equal(parseDuration('5s'), 5000);
  assert.equal(parseDuration('100ms'), 100);
  assert.equal(parseDuration('1m'), 60000);
  assert.equal(parseDuration('bogus', 42), 42);
});
