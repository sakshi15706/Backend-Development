'use strict';
const express = require('express');
const { Recorder } = require('./lib/metrics');

/**
 * Bottleneck switches, read PER REQUEST from the environment so experiments need no code edits:
 *   PING_DELAY_MS  async wait, like a slow database call   (slide Task 3: await setTimeout 50)
 *   PING_BLOCK_MS  synchronous busy loop that blocks the event loop (the other classic bottleneck)
 */
const num = (name) => Number(process.env[name] || 0);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function blockFor(ms) { const end = performance.now() + ms; while (performance.now() < end) { /* CPU busy */ } }

function createApp({ recorder = new Recorder().start() } = {}) {
  const app = express();
  app.disable('x-powered-by');
  app.use(recorder.middleware());                       // Task 1: instrument every route

  app.get('/api/ping', async (req, res) => {
    if (num('PING_DELAY_MS')) await sleep(num('PING_DELAY_MS'));
    if (num('PING_BLOCK_MS')) blockFor(num('PING_BLOCK_MS'));
    res.json({ ok: true });
  });

  // PBL endpoint: a small in-memory "attendance" list. Serialising a big array is real CPU work.
  const records = Array.from({ length: Number(process.env.ATTENDANCE_ROWS || 200) }, (_, i) => ({
    studentId: `S${100 + i}`, classId: 'class-5A', present: i % 7 !== 0, at: 1730000000000 + i,
  }));
  app.get('/api/attendance', async (req, res) => {
    if (num('PING_DELAY_MS')) await sleep(num('PING_DELAY_MS'));
    res.json(records);
  });

  app.get('/api/error', (req, res) => res.status(500).json({ error: 'deliberate' }));     // for the error-rate metric

  app.get('/metrics', (req, res) => res.json(recorder.snapshot({ path: req.query.path })));
  app.post('/metrics/reset', (req, res) => { recorder.reset(); res.json({ reset: true }); });

  app.recorder = recorder;
  return app;
}

module.exports = { createApp };
