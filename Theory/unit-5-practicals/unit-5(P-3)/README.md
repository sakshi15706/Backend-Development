# Unit 5 (P-3): Performance Profiling in Express and FastAPI (Lecture 58)

**PBL:** instrument one SMS endpoint, capture baseline metrics under load (`autocannon -c 50 -d 30`), and write a one-page report that names the top bottleneck with evidence.

## Setup
```bash
cd "unit-5(P-3)"
npm install
npm test                        # 19 Express tests
npm start                       # http://localhost:3000   (/api/ping, /api/attendance, /metrics)
npm run loadtest                # npx autocannon -c 50 -d 30 http://localhost:3000/api/ping
npm run experiment              # five scenarios, fresh server each, writes results/experiment.md + .json

# FastAPI version
cd fastapi-app
pip install -r requirements.txt
python -m pytest -q             # 9 tests
uvicorn main:app --port 3200    # then: npx autocannon -c 50 -d 30 http://localhost:3200/api/ping
```

## Slide task to file
| Slide | Files |
|---|---|
| 3.1 `perf_hooks` middleware and `/metrics` | `express-app/lib/metrics.js`, `express-app/app.js` |
| 3.3 event-loop delay | `/metrics` field `eventLoopDelayMs` |
| 4.1 FastAPI timing middleware | `fastapi-app/main.py`, `fastapi-app/metrics.py` |
| Task 1 instrument and check count, p50, p95, p99 | tests in both apps |
| Task 2 load test, four metrics, compare p99 | `scripts/run-experiment.js`, `results/` |
| Task 3 deliberate bottleneck | `PING_DELAY_MS=50 npm start` (await) and `PING_BLOCK_MS=5 npm start` (CPU block): no code edits needed |
| PBL one-page report | `PROFILING_REPORT.md` (worked example plus your own template) |
| k6 with a threshold | `loadtest/k6-ping.js` (**not run**: k6 was not installed here) |

## What was measured (sandbox, 50 connections, 30 s, warm-up discarded)
| Scenario | req/s | client p99 | what it shows |
|---|---|---|---|
| baseline `/api/ping` | ~9,900 | 12 ms | two runs agree within about 2% |
| + 50 ms `await` | 972 | 56 ms | latency rises by about 50 ms: the handler is the bottleneck, event loop stays healthy |
| + 5 ms CPU block | 189 | 512 ms | single thread blocked: throughput ceiling 1 / 5 ms, event-loop delay p99 about 252 ms |
| `/api/attendance` (200 rows) | 5,917 | 16 ms | JSON serialisation costs real CPU |

FastAPI (single uvicorn worker, 15 s): `/api/ping` 3,313 req/s; 50 ms `time.sleep` inside `async def` only **18 req/s** (it blocks the event loop); the same wait in a plain `def` **775 req/s** (runs in a thread pool). Full tables: `results/`.

## Things the slides do not say (and I found while testing)
1. **Percentile rule.** The slide's `sorted[floor(n * p)]` returns the **maximum** for p99 when there are 100 samples. The code uses nearest-rank (`ceil(p * n) - 1`).
2. **`monitorEventLoopDelay` has a floor.** It samples a timer every `resolution` ms, so an *idle* loop reports about 20 ms with `resolution: 20`. The metric here subtracts the resolution (the "~50 ms" warning level in the slide then means excess delay). Raw values would mislead you.
3. **`/metrics` and autocannon will not agree.** The slide says their p99 "should be close". They measure different things (see `PROFILING_REPORT.md`). Under event-loop blocking in Express the server-side timer does not even see the queueing; in FastAPI the same blocking shows up in the server-side numbers as well (1.9 s p50 in scenario G), because of where each timer starts. I measured both; I did not separately verify the cause beyond that.
4. **The window.** `/metrics` keeps the last 1000 requests. After a 30 s test it describes only the tail end of the run.
5. **`/metrics` is excluded from its own stats**, and error rate counts only 5xx.
6. **Cumulative counters** (`totalRequests`, `errors`, `errorRate`) are not limited by the window.
7. **Do not compare frameworks from this data.** The slide's "FastAPI 180 RPS vs Express 880 RPS" comparison and my numbers differ because they measure different things; mine has the load generator on the same 2 vCPUs, one uvicorn worker, and trivial endpoints. The skill here is measuring your own endpoint.

## Not done / not verified
- **`bodhi-node-profiler`, `node-runtime-monitor`, `fastapi-profiler-lite`, `asgi-profiler`** are not installed or tested. I could not verify their current APIs; the hand-written middleware needs no dependency and is what the tests cover. If you add one, record what you ran.
- **k6** script written but not run.
- **CPU/memory over time** (leaks) needs a longer run; this reports a point-in-time snapshot.

## Viva points
- Four metrics: latency percentiles, throughput, error rate, resource usage. Never report only the mean (`the mean hides a bad tail` test).
- p99 = 120 ms means 1 request in 100 took longer than 120 ms.
- Throughput vs latency: with 50 connections and a 50 ms handler, the ceiling is 50 / 0.05 = 1000 req/s (measured 972).
- Async delay vs blocking: await keeps the event loop free; a synchronous loop (or `time.sleep` in `async def`) stops every other request.
- A single test is one sample: repeat it and report the spread; discard the warm-up.
