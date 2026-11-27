'use strict';
/**
 * A very small Attendance service (plain http, no framework) with:
 *   GET  /health          -> 200 {"status":"UP"}   or 503 while "failing" (what Consul probes)
 *   POST /health/fail     -> make /health fail     (Task 1 checkpoint: simulate a broken instance)
 *   POST /health/recover  -> make /health pass again
 *   POST /attendance      -> publish attendance.marked, answer 202 {"eventId": ...}
 */
const http = require('http');
const { randomUUID } = require('crypto');

function startAttendanceService({ port = 4001, host = '127.0.0.1', publish }) {
  let failing = false;

  const server = http.createServer((req, res) => {
    const json = (code, body) => { res.writeHead(code, { 'content-type': 'application/json' }); res.end(JSON.stringify(body)); };
    let raw = '';
    req.on('data', (c) => { raw += c; if (raw.length > 10_000) req.destroy(); });      // small bodies only
    req.on('end', async () => {
      const { pathname } = new URL(req.url, 'http://x');

      if (req.method === 'GET' && pathname === '/health') return failing ? json(503, { status: 'DOWN' }) : json(200, { status: 'UP' });
      if (req.method === 'POST' && pathname === '/health/fail') { failing = true; return json(200, { failing }); }
      if (req.method === 'POST' && pathname === '/health/recover') { failing = false; return json(200, { failing }); }

      if (req.method === 'POST' && pathname === '/attendance') {
        let body;
        try { body = JSON.parse(raw); } catch { return json(400, { error: 'invalid JSON' }); }
        if (!body.studentId || !body.classId || typeof body.present !== 'boolean') {
          return json(400, { error: 'studentId, classId and present (true/false) are required' });
        }
        const event = {
          eventId: body.eventId || randomUUID(),      // a client may resend the same eventId (retries)
          type: 'attendance.marked',
          classId: body.classId, studentId: body.studentId, present: body.present, at: Date.now(),
        };
        try {
          await publish(event);
        } catch (err) {
          return json(503, { error: 'event broker unavailable' });
        }
        return json(202, { eventId: event.eventId });
      }
      json(404, { error: 'not found' });
    });
  });

  return new Promise((resolve) => server.listen(port, host, () => resolve({
    port: server.address().port,
    isFailing: () => failing,
    close: () => new Promise((r) => server.close(r)),
  })));
}

module.exports = { startAttendanceService };

// node services/attendance-service.js   (needs RabbitMQ; registers itself in Consul when CONSUL_URL is set)
if (require.main === module) {
  const { publishAttendanceMarked } = require('../broker/producer');
  const { registerService, deregisterService } = require('../registry/consul-client');
  const port = Number(process.env.PORT || 4001);
  startAttendanceService({ port, publish: (e) => publishAttendanceMarked(e) }).then(async (svc) => {
    console.log(`attendance service on http://127.0.0.1:${svc.port}`);
    if (process.env.CONSUL_URL) {
      const id = `attendance-${svc.port}`;
      await registerService({ name: 'attendance', id, port: svc.port });
      console.log(`registered ${id} in Consul`);
      const bye = async () => { await deregisterService(id).catch(() => {}); process.exit(0); };
      process.on('SIGINT', bye); process.on('SIGTERM', bye);        // deregister on shutdown
    }
  });
}
