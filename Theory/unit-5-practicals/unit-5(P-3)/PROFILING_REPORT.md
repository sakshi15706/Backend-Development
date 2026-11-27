# One-page profiling report: SMS API (Lecture 58 PBL)

> **How to read this page.** Section A is a *worked example*: real numbers I measured in my sandbox with the scripts in this folder, to show what a finished report looks like. The bottleneck in it was **introduced on purpose** (Task 3). Your own report must come from your machine, your endpoint and your numbers: run `npm run experiment` and fill in section B.

## A. Worked example (measured in my sandbox)
**Setup:** Express app in `express-app/`, Node v22, 2 vCPU Intel Xeon @ 2.10 GHz, load generator **on the same machine** (so they compete for CPU). autocannon `-c 50 -d 30`, 3 s warm-up discarded, fresh server per scenario. Full raw data: `results/experiment.json`.

**Endpoint tested:** `GET /api/attendance` (200 rows, serialised as JSON).

| Metric | Value |
|---|---|
| Throughput | **5,917 req/s** |
| Latency p50 / p99 (client, autocannon) | 7 ms / 16 ms |
| Latency p50 / p95 / p99 (server, middleware) | 0.116 / 0.203 / 0.282 ms |
| Error rate | 0 errors in about 177,000 requests |
| Event-loop delay p99 over baseline | 11.9 ms |
| Memory | RSS 131.9 MB |

**Repeatability (checkpoint "run the same test twice"):** baseline `/api/ping`, run 1 vs run 2: 9,980 vs 9,762 req/s; client p99 12 ms vs 12 ms; server p99 0.259 vs 0.255 ms. About 2% difference in throughput, so one run is a sample, not a fact; repeat at least twice and quote the spread.

**Bottleneck experiments on `/api/ping` (Task 3):**

| Scenario | req/s | client p50 | client p99 | server p99 | event-loop p99 over baseline |
|---|---|---|---|---|---|
| baseline | 9,980 | 4 ms | 12 ms | 0.26 ms | 8.8 ms |
| + 50 ms `await` (slow "database") | 972 | 51 ms | 56 ms | 54.6 ms | 2.8 ms |
| + 5 ms synchronous CPU block | 189 | 260 ms | **512 ms** | 5.5 ms | **252 ms** |

**Identified bottleneck and evidence (for the introduced 5 ms blocking loop):** event-loop delay p99 rose to about 252 ms while the handler itself took only about 5 ms server-side, and throughput collapsed from about 10,000 to 189 req/s (about 1 / 5 ms = 200 per second: one request at a time). Requests queue *before* the handler runs, so the server-side timer does not see the wait. Evidence = event-loop delay + throughput ceiling + gap between client p99 (512 ms) and server p99 (5.5 ms).
For the **50 ms await**: client p50 moves from 4 ms to 51 ms (about +47 ms, as the slide predicts) and event-loop delay stays low: the handler is the bottleneck, not the loop. Throughput is about 50 / 0.05 = 1000 req/s, which is the 50-connection limit.

**Interpretation notes**
- *p99 = 56 ms* means 1 request in 100 took longer than 56 ms. The mean would hide this; never report only the mean.
- The slide says `/metrics` p99 and autocannon p99 "should be close". Here they are **not** (0.26 ms vs 12 ms), and that is expected: autocannon measures from send to full response (network stack, kernel queues, its own CPU use), the middleware measures only the time Express spends on the request. Compare them as a **gap**: a large gap means time is lost *outside* the handler (queueing, the load generator, the network). `/metrics` also covers only the last 1,000 requests.
- Load generator and server share 2 vCPUs here, so absolute numbers are lower than on a dedicated setup. Use them for **relative** comparison.

## B. Your report (fill in)
| Item | Your value |
|---|---|
| Endpoint tested | |
| Date, machine (CPU, RAM), Node/Python version | |
| Command | `npx autocannon -c 50 -d 30 http://localhost:3000/...` |
| Throughput (req/s) | |
| Latency p50 / p95 / p99 | |
| Error rate | |
| CPU / memory | |
| Event-loop delay p99 | |
| Runs repeated (n) and spread | |
| **Top bottleneck** | |
| **Evidence** (numbers, not intuition) | |
| Proposed fix (do not apply before measuring again) | |
