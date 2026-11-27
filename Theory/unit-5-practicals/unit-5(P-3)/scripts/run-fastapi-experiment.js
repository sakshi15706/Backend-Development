'use strict';
/**
 * node scripts/run-fastapi-experiment.js [durationSeconds=15]
 * Starts uvicorn for fastapi-app (PYTHON env var = interpreter, default "python") and load-tests three endpoints.
 * Results: results/fastapi.md. NOT a framework comparison: see README.
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const autocannon = require('autocannon');

const DURATION = Number(process.argv[2] || 15);
const PORT = 3200;
const PY = process.env.PYTHON || 'python';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const get = (p, method = 'GET') => fetch(`http://127.0.0.1:${PORT}${p}`, { method }).then((r) => r.json());

const SCENARIOS = [
  { name: 'F. /api/ping', url: '/api/ping' },
  { name: 'G. 50 ms time.sleep inside `async def` (blocks the loop)', url: '/api/blocking-in-async' },
  { name: 'H. 50 ms time.sleep inside plain `def` (thread pool)', url: '/api/blocking-in-sync' },
];

(async () => {
  const child = spawn(PY, ['-m', 'uvicorn', 'main:app', '--port', String(PORT), '--log-level', 'warning'], {
    cwd: path.join(__dirname, '..', 'fastapi-app'), stdio: 'ignore',
  });
  const rows = [];
  try {
    for (let i = 0; i < 80; i++) { try { await get('/metrics'); break; } catch { await sleep(150); } }
    for (const s of SCENARIOS) {
      await autocannon({ url: `http://127.0.0.1:${PORT}${s.url}`, connections: 50, duration: 3 });   // warm-up, discarded
      await get('/metrics/reset', 'POST');
      const r = await autocannon({ url: `http://127.0.0.1:${PORT}${s.url}`, connections: 50, duration: DURATION });
      const m = await get(`/metrics?path=${s.url}`);
      rows.push(`| ${s.name} | ${Math.round(r.requests.average)} | ${r.latency.p50} | ${r.latency.p99} | ${m.p50} / ${m.p95} / ${m.p99} | ${r.errors + r.non2xx} |`);
      console.log(rows[rows.length - 1]);
    }
  } finally { child.kill(); }
  const md = [`${DURATION} s per scenario after a 3 s warm-up, 50 connections, uvicorn single worker.`, '',
    '| Scenario | req/s | client p50 (ms) | client p99 (ms) | server p50 / p95 / p99 (ms) | errors |', '|---|---|---|---|---|---|', ...rows, ''].join('\n');
  fs.writeFileSync(path.join(__dirname, '..', 'results', 'fastapi.md'), md);
})().catch((e) => { console.error(e); process.exit(1); });
