15 s per scenario after a 3 s warm-up, 50 connections, uvicorn single worker.

| Scenario | req/s | client p50 (ms) | client p99 (ms) | server p50 / p95 / p99 (ms) | errors |
|---|---|---|---|---|---|
| F. /api/ping | 3313 | 13 | 37 | 7.12 / 9.305 / 9.643 | 0 |
| G. 50 ms time.sleep inside `async def` (blocks the loop) | 18 | 2550 | 8682 | 1887.262 / 1991.852 / 1992.369 | 0 |
| H. 50 ms time.sleep inside plain `def` (thread pool) | 775 | 63 | 83 | 62.734 / 68.6 / 69.644 | 0 |
