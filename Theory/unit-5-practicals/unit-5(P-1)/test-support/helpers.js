'use strict';
const http = require('http');

/** Wrap a (req,res) Functions-Framework style handler in a real HTTP server on a free port. */
function serveFunction(fn) {
  const server = http.createServer((req, res) => {
    let raw = '';
    req.on('data', (c) => { raw += c; });
    req.on('end', () => {
      try { req.body = raw ? JSON.parse(raw) : {}; } catch { req.body = undefined; }
      res.status = (code) => { res.statusCode = code; return res; };
      res.json = (obj) => { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(obj)); return res; };
      Promise.resolve(fn(req, res)).catch(() => { res.statusCode = 500; res.end(); });
    });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({
    url: `http://127.0.0.1:${server.address().port}`,
    close: () => new Promise((r) => server.close(r)),
  })));
}

/** Poll until fn() returns truthy (used while waiting for a health-check interval to pass). */
async function waitFor(fn, { timeout = 3000, step = 20 } = {}) {
  const start = Date.now();
  for (;;) {
    const value = await fn();
    if (value) return value;
    if (Date.now() - start > timeout) throw new Error('waitFor timed out');
    await new Promise((r) => setTimeout(r, step));
  }
}

const silent = { info() {}, error() {}, log() {} };
const sample = (over = {}) => ({ eventId: 'evt-0001', type: 'attendance.marked', classId: 'class-5A', studentId: 'S102', present: true, at: 1730000000000, ...over });

module.exports = { serveFunction, waitFor, silent, sample };
