'use strict';
/**
 * A minimal stand-in for a Consul agent, so Task 1 can be tried without Docker.
 * Implements ONLY what this practical uses:
 *   GET  /v1/status/leader
 *   PUT  /v1/agent/service/register
 *   PUT  /v1/agent/service/deregister/<id>
 *   GET  /v1/health/service/<name>[?passing=true]
 * and, like Consul, runs each registered HTTP health check on its Interval: a service is
 * "critical" until its first successful check and again whenever a check fails or times out.
 * It is NOT Consul (no clustering, KV store, DNS interface, ACLs, ...). For the real thing use
 *   docker run -d --name sms-consul -p 8500:8500 consul agent -dev -client=0.0.0.0
 */
const http = require('http');

function parseDuration(text, fallbackMs) {
  const m = /^(\d+(?:\.\d+)?)(ms|s|m)$/.exec(String(text || ''));
  if (!m) return fallbackMs;
  return Number(m[1]) * { ms: 1, s: 1000, m: 60000 }[m[2]];
}

function startMockConsul({ port = 8500, host = '127.0.0.1' } = {}) {
  const services = new Map();          // id -> { service, status, timer }

  async function runCheck(entry) {
    const { Check } = entry.service;
    if (!Check || !Check.HTTP) { entry.status = 'passing'; return; }
    try {
      const res = await fetch(Check.HTTP, { signal: AbortSignal.timeout(parseDuration(Check.Timeout, 1000)) });
      entry.status = res.status >= 200 && res.status < 300 ? 'passing' : 'critical';   // Consul: 2xx passing
    } catch {
      entry.status = 'critical';
    }
  }

  function register(service) {
    const old = services.get(service.ID);
    if (old) clearInterval(old.timer);
    const entry = { service, status: 'critical', timer: null };     // critical until the first check passes
    services.set(service.ID, entry);
    runCheck(entry);
    entry.timer = setInterval(() => runCheck(entry), parseDuration(service.Check && service.Check.Interval, 10000));
    entry.timer.unref();
  }

  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://x');
    const json = (code, body) => { res.writeHead(code, { 'content-type': 'application/json' }); res.end(JSON.stringify(body)); };
    let raw = '';
    req.on('data', (c) => { raw += c; });
    req.on('end', () => {
      if (req.method === 'GET' && url.pathname === '/v1/status/leader') return json(200, '127.0.0.1:8300');

      if (req.method === 'PUT' && url.pathname === '/v1/agent/service/register') {
        let body;
        try { body = JSON.parse(raw); } catch { res.writeHead(400); return res.end('invalid JSON'); }
        if (!body.Name) { res.writeHead(400); return res.end('Missing service Name'); }
        body.ID = body.ID || body.Name;
        register(body);
        res.writeHead(200); return res.end();
      }

      const dereg = /^\/v1\/agent\/service\/deregister\/(.+)$/.exec(url.pathname);
      if (req.method === 'PUT' && dereg) {
        const id = decodeURIComponent(dereg[1]);
        const entry = services.get(id);
        if (!entry) { res.writeHead(404); return res.end(`Unknown service ID "${id}"`); }
        clearInterval(entry.timer); services.delete(id);
        res.writeHead(200); return res.end();
      }

      const health = /^\/v1\/health\/service\/(.+)$/.exec(url.pathname);
      if (req.method === 'GET' && health) {
        const name = decodeURIComponent(health[1]);
        const onlyPassing = url.searchParams.get('passing') === 'true';
        const rows = [...services.values()]
          .filter((e) => e.service.Name === name && (!onlyPassing || e.status === 'passing'))
          .map((e) => ({
            Node: { Node: 'mock-node' },
            Service: { ID: e.service.ID, Service: e.service.Name, Address: e.service.Address, Port: e.service.Port },
            Checks: [{ Status: e.status, ServiceID: e.service.ID }],
          }));
        return json(200, rows);
      }
      res.writeHead(404); res.end('not found');
    });
  });

  return new Promise((resolve) => {
    server.listen(port, host, () => resolve({
      port: server.address().port,
      url: `http://${host}:${server.address().port}`,
      close: () => new Promise((r) => { for (const e of services.values()) clearInterval(e.timer); server.close(r); }),
    }));
  });
}

module.exports = { startMockConsul, parseDuration };

if (require.main === module) {
  startMockConsul({ port: Number(process.env.PORT || 8500) }).then((c) => console.log(`mock Consul listening on ${c.url}`));
}
