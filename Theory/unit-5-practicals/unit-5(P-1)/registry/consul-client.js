'use strict';
/**
 * Task 1: talk to Consul's HTTP API (works with a real Consul agent or with mock-consul.js).
 * Uses Node's built-in fetch (Node 18+), so no node-fetch dependency is needed.
 */
const BASE = () => process.env.CONSUL_URL || 'http://localhost:8500';

/** What a service does at startup: announce name, address, port and a health check. */
async function registerService({ name, id, address = '127.0.0.1', port, healthPath = '/health', interval = '5s', timeout = '1s', base = BASE() }) {
  const body = {
    Name: name,
    ID: id,
    Address: address,
    Port: port,
    Check: { HTTP: `http://${address}:${port}${healthPath}`, Interval: interval, Timeout: timeout },
  };
  const res = await fetch(`${base}/v1/agent/service/register`, { method: 'PUT', body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`register failed: ${res.status} ${await res.text()}`);
}

/** What a service does on shutdown. */
async function deregisterService(id, { base = BASE() } = {}) {
  const res = await fetch(`${base}/v1/agent/service/deregister/${encodeURIComponent(id)}`, { method: 'PUT' });
  if (!res.ok) throw new Error(`deregister failed: ${res.status}`);
}

/** Lookup: only instances whose health checks are passing (?passing=true). */
async function discoverHealthy(name, { base = BASE() } = {}) {
  const res = await fetch(`${base}/v1/health/service/${encodeURIComponent(name)}?passing=true`);
  if (!res.ok) throw new Error(`discover failed: ${res.status}`);
  const instances = await res.json();
  return instances.map((i) => ({ id: i.Service.ID, address: i.Service.Address, port: i.Service.Port }));
}

/**
 * Client-side discovery: the client asks the registry and load-balances itself
 * (here: round-robin). With server-side discovery a router/gateway would do this instead.
 */
function roundRobin() {
  let next = 0;
  return (instances) => {
    if (!instances.length) throw new Error('no healthy instances available');
    return instances[next++ % instances.length];
  };
}

module.exports = { registerService, deregisterService, discoverHealthy, roundRobin };

// node registry/consul-client.js discover attendance
if (require.main === module) {
  const [cmd, name] = process.argv.slice(2);
  if (cmd === 'discover') {
    discoverHealthy(name || 'attendance').then((list) => {
      console.log('healthy attendance instances:', list.map((i) => `${i.address}:${i.port}`));
    }).catch((e) => { console.error(e.message); process.exit(1); });
  } else {
    console.log('usage: node registry/consul-client.js discover <service-name>');
  }
}
