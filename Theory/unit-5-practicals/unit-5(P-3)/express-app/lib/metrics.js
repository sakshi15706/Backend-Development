'use strict';
/**
 * Latency / error / resource recorder (Lecture 58, section 3).
 *
 * Slide version: keep the last 1000 request durations in an array and compute percentiles on
 * demand. Same idea here, with three corrections:
 *   - percentiles use the nearest-rank rule (index = ceil(p * n) - 1); the slide's
 *     floor(n * p) returns the MAXIMUM for p99 when n = 100;
 *   - errors and the total request count are cumulative counters, so the error rate is not
 *     limited to the 1000-sample window;
 *   - /metrics itself is not recorded, so reading the metrics never changes them.
 * NOTE the window: after a long load test /metrics describes only the LAST `windowSize`
 * requests. The load generator's own report covers the whole run; compare with that in mind.
 */
const { performance, monitorEventLoopDelay } = require('perf_hooks');

function percentile(sortedAscending, p) {
  if (!sortedAscending.length) return 0;
  const rank = Math.ceil(p * sortedAscending.length);
  return sortedAscending[Math.min(Math.max(rank, 1), sortedAscending.length) - 1];
}

class Recorder {
  constructor({ windowSize = 1000, ignorePaths = ['/metrics', '/metrics/reset'], eventLoopResolution = 20 } = {}) {
    this.windowSize = windowSize;
    this.ignorePaths = new Set(ignorePaths);
    this.resolution = eventLoopResolution;
    this.eventLoop = monitorEventLoopDelay({ resolution: eventLoopResolution });
    this.reset();
  }

  reset() {
    this.samples = [];              // [{ path, duration, status }], newest last, at most windowSize
    this.total = 0;                 // cumulative since reset
    this.errors = 0;                // status >= 500 (server errors)
    this.startedAt = performance.now();
    this.eventLoop.reset();
  }

  start() { this.eventLoop.enable(); return this; }
  stop() { this.eventLoop.disable(); }

  /** Express middleware */
  middleware() {
    return (req, res, next) => {
      if (this.ignorePaths.has(req.path)) return next();
      const start = performance.now();
      res.on('finish', () => this.record(req.path, performance.now() - start, res.statusCode));
      next();
    };
  }

  record(path, duration, status) {
    this.samples.push({ path, duration, status });
    if (this.samples.length > this.windowSize) this.samples.shift();   // bound the memory
    this.total++;
    if (status >= 500) this.errors++;
  }

  snapshot({ path } = {}) {
    const window = path ? this.samples.filter((s) => s.path === path) : this.samples;
    const sorted = window.map((s) => s.duration).sort((a, b) => a - b);
    const seconds = (performance.now() - this.startedAt) / 1000;
    const mem = process.memoryUsage();
    // monitorEventLoopDelay samples a timer that fires every `resolution` ms, so an IDLE loop reports
    // about `resolution` (20 ms here). The real delay is what is OVER that baseline.
    const ms = (ns) => Number(Math.max(0, ns / 1e6 - this.resolution).toFixed(3));
    const round = (n) => Number(n.toFixed(3));
    return {
      count: sorted.length,                              // samples in the window
      p50: round(percentile(sorted, 0.50)),
      p95: round(percentile(sorted, 0.95)),
      p99: round(percentile(sorted, 0.99)),
      max: round(sorted.length ? sorted[sorted.length - 1] : 0),
      mean: round(sorted.length ? sorted.reduce((a, b) => a + b, 0) / sorted.length : 0),   // shown only to demonstrate why mean alone hides the tail
      totalRequests: this.total,
      errors: this.errors,
      errorRate: this.total ? round((this.errors / this.total) * 100) : 0,    // percent
      requestsPerSecond: seconds > 0 ? round(this.total / seconds) : 0,
      window: this.windowSize,
      eventLoopDelayMs: {                                // Node.js leading indicator, excess over the timer resolution
        mean: ms(this.eventLoop.count ? this.eventLoop.mean : 0),
        p99: ms(this.eventLoop.percentile(99)),
        max: ms(this.eventLoop.max),
      },
      memory: { rssMB: round(mem.rss / 1048576), heapUsedMB: round(mem.heapUsed / 1048576) },
      cpuSeconds: round((process.cpuUsage().user + process.cpuUsage().system) / 1e6),
    };
  }
}

module.exports = { Recorder, percentile };
