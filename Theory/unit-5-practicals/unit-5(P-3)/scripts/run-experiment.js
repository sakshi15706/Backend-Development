'use strict';
/**
 * node scripts/run-experiment.js [durationSeconds=30] [connections=50]
 *
 * Repeatable measurement (CO4): for each scenario it starts a FRESH server process, warms it up,
 * resets /metrics, runs autocannon (-c 50 -d 30 like the slide), then reads /metrics and records:
 *   throughput (req/s), latency p50 / p99 (autocannon, client side), p50/p95/p99 (our middleware,
 *   server side), errors, event-loop delay, memory.
 * Results go to results/experiment.json and results/experiment.md.
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const autocannon = require('autocannon');

const DURATION = Number(process.argv[2] || 30);
const CONNECTIONS = Number(process.argv[3] || 50);
const WARMUP = 3;
const PORT = 3100;

const SCENARIOS = [
  { name: 'A. baseline /api/ping (run 1)', url: '/api/ping', env: {} },
  { name: 'B. baseline /api/ping (run 2, same settings)', url: '/api/ping', env: {} },
  { name: 'C. /api/ping + 50 ms await (slow "database")', url: '/api/ping', env: { PING_DELAY_MS: '50' } },
  { name: 'D. /api/ping + 5 ms synchronous CPU block', url: '/api/ping', env: { PING_BLOCK_MS: '5' } },
  { name: 'E. /api/attendance (PBL endpoint, 200 rows)', url: '/api/attendance', env: {} },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const get = (p, method = 'GET') => fetch(`http://127.0.0.1:${PORT}${p}`, { method }).then((r) => r.json());

async function waitUp() {
  for (let i = 0; i < 50; i++) { try { await get('/metrics'); return; } catch { await sleep(100); } }
  throw new Error('server did not start');
}

async function run(scenario) {
  const child = spawn(process.execPath, [path.join(__dirname, '..', 'express-app', 'server.js')], {
    env: { ...process.env, PORT: String(PORT), ...scenario.env }, stdio: 'ignore',
  });
  try {
    await waitUp();
    // warm-up: JIT, connection pools and caches settle; its numbers are thrown away
    await autocannon({ url: `http://127.0.0.1:${PORT}${scenario.url}`, connections: CONNECTIONS, duration: WARMUP });
    await get('/metrics/reset', 'POST');
    const r = await autocannon({ url: `http://127.0.0.1:${PORT}${scenario.url}`, connections: CONNECTIONS, duration: DURATION });
    const server = await get(`/metrics?path=${scenario.url}`);
    return {
      scenario: scenario.name, endpoint: scenario.url, connections: CONNECTIONS, durationSeconds: DURATION,
      reqPerSec: Math.round(r.requests.average),
      totalRequests: r.requests.total,
      client: { p50: r.latency.p50, p97_5: r.latency.p97_5, p99: r.latency.p99, max: r.latency.max, mean: Number(r.latency.average.toFixed(2)) },
      server: { p50: server.p50, p95: server.p95, p99: server.p99, mean: server.mean, windowSamples: server.count },
      errors: r.errors + r.non2xx, timeouts: r.timeouts,
      eventLoopP99Ms: server.eventLoopDelayMs.p99, eventLoopMaxMs: server.eventLoopDelayMs.max,
      cpuSeconds: server.cpuSeconds, rssMB: server.memory.rssMB,
    };
  } finally {
    child.kill();
    await sleep(300);
  }
}

(async () => {
  const results = [];
  for (const s of SCENARIOS) {
    process.stdout.write(`running ${s.name} (${WARMUP}s warm-up + ${DURATION}s) ... `);
    const r = await run(s);
    results.push(r);
    console.log(`${r.reqPerSec} req/s, client p99 ${r.client.p99} ms`);
  }
  fs.mkdirSync(path.join(__dirname, '..', 'results'), { recursive: true });
  const meta = { node: process.version, cpus: require('os').cpus().length, cpuModel: require('os').cpus()[0].model, date: new Date().toISOString() };
  fs.writeFileSync(path.join(__dirname, '..', 'results', 'experiment.json'), JSON.stringify({ meta, results }, null, 2));

  const f = (n) => String(n);
  const rows = results.map((r) => `| ${r.scenario} | ${r.reqPerSec} | ${f(r.client.p50)} | ${f(r.client.p99)} | ${f(r.server.p50)} / ${f(r.server.p95)} / ${f(r.server.p99)} | ${r.errors} | ${f(r.eventLoopP99Ms)} | ${f(r.rssMB)} |`);
  const md = [
    `Measured on: ${meta.cpuModel} x${meta.cpus}, Node ${meta.node}, ${meta.date}`,
    `Settings: ${CONNECTIONS} connections, ${DURATION} s per scenario after a ${WARMUP} s warm-up (discarded), fresh server process per scenario.`, '',
    '| Scenario | req/s | client p50 (ms) | client p99 (ms) | server p50 / p95 / p99 (ms) | errors | event-loop p99 over baseline (ms) | RSS (MB) |',
    '|---|---|---|---|---|---|---|---|', ...rows, '',
  ].join('\n');
  fs.writeFileSync(path.join(__dirname, '..', 'results', 'experiment.md'), md);
  console.log('\n' + md);
})().catch((e) => { console.error(e); process.exit(1); });
