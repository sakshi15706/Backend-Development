# Backend Development Lab Report: Unit 5 (Advanced Topics)

| | |
|---|---|
| Name | _(your name)_ |
| SAP ID / Roll no. | _(your SAP ID)_ |
| Course | Backend Development, UPES (CO4, CO5) |
| Source | Unit 5 lecture slides by Dr. Prateek Raj Gautam |
| Folders | `unit-5(P-1)` to `unit-5(P-4)` inside `Theory` |

## 1. Summary
| Practical | Lectures | Topic | Verification run in my environment |
|---|---|---|---|
| P-1 | 52-54 | Service discovery (Consul), RabbitMQ events with an idempotent consumer, serverless function | 45 tests pass (`node --test`); `npm run demo` runs the whole flow |
| P-2 | 55-57 | AWS Lambda consumer behind SQS, DynamoDB idempotency, least-privilege role, anti-pattern audit | 32 tests pass; `cfn-lint` clean on the SAM template |
| P-3 | 58 | Profiling: latency percentiles, throughput, error rate, bottlenecks in Express and FastAPI | 19 Express tests and 9 FastAPI tests pass; load tests run with autocannon |
| P-4 | 59 | Presentation architecture and evidence | no code; preparation kit with a worked example and a review rubric |

Unit 5 in the slides is "Advanced Topics". The Unit 4 slides (WebSockets, Socket.io, microservices) were not part of what I received, so there is no Unit 4 folder.

## 2. Practical details

### P-1: Discovery, messaging and serverless (Lectures 52-54)
- **Registry:** a Consul client (register with an HTTP health check, deregister on shutdown, discover `?passing=true`, round-robin). Test of the checkpoint: when `/health` fails, the instance disappears from the passing list, and returns after recovery.
- **Messaging:** producer (durable queue, persistent messages) and a consumer that remembers `eventId`s. Publishing the same event twice produces one notification.
- **Serverless:** a stateless e-mail function (Functions Framework entry point, dry-run unless `MAIL_API_URL` is set) fed by a bridge from the broker.
- **PBL documents:** `docs/ARCHITECTURE.md` has the architecture diagram, client vs server-side discovery choice, a sync/async classification of eight SMS interactions, the serverless migration rationale, and review questions.
- **Improvement over the slide:** the slide stores the `eventId` before processing, so a failure after that point loses the event on redelivery; here it is stored after success, and a test demonstrates the slide's problem.
- **Stand-ins:** the environment had no Docker, RabbitMQ or Consul, so the tests use `lib/fake-amqp.js` and `registry/mock-consul.js`. The application code is unchanged for real services, but I have **not** run it against real RabbitMQ or Consul.

### P-2: AWS Lambda backend (Lectures 55-57)
- **Handler** (`src/index.mjs`): SQS batch to DynamoDB with `attribute_not_exists(eventId)`. A duplicate raises `ConditionalCheckFailedException`, which the handler treats as success (the slide's code does not catch it, so duplicates would fail the batch). It returns a partial batch response (`batchItemFailures`), sends poison messages to the DLQ path, and hands back unprocessed records when time runs short.
- **Infrastructure** (`template.yaml`): SQS queue with a DLQ (`maxReceiveCount` 3), DynamoDB table keyed on `eventId`, function with a policy of **one action (`dynamodb:PutItem`) on one table ARN**, `ReportBatchItemFailures` enabled, function timeout (10 s) shorter than the queue visibility timeout (60 s).
- **Tests:** duplicate event leaves one item; a throttled write fails only its own record; without `PutItem` every record reports `AccessDeniedException`; the template has no wildcard action or resource; the function never writes to its own trigger.
- **Documents:** anti-pattern audit (recursion and synchronous waits, with a worked bad example and fix each), SaaS/PaaS/FaaS classification of the SMS components, and AWS deployment steps.
- **Runtime:** the slide uses `nodejs20.x`; when I checked the AWS runtimes page (24 Nov 2026) it was no longer in the supported table, so the template uses `nodejs22.x`. Re-check before deploying.
- **Not done:** the real AWS deployment (needs your account), `sam local invoke` (needs Docker; `npm run invoke:local` is a stand-in for the handler logic only), and the IAM console inspection.

### P-3: Performance profiling (Lecture 58)
`perf_hooks` middleware with `/metrics` (p50/p95/p99, max, mean, throughput, error rate, event-loop delay, memory), the same in FastAPI, bottleneck switches without code edits, a repeatable experiment script (fresh server, warm-up discarded, autocannon `-c 50 -d 30`) and a one-page report. Measured on my sandbox (2 vCPU, load generator on the same machine):

| Scenario | req/s | client p50 | client p99 | event-loop p99 over baseline |
|---|---|---|---|---|
| baseline `/api/ping`, run 1 | 9,980 | 4 ms | 12 ms | 8.8 ms |
| baseline, run 2 | 9,762 | 4 ms | 12 ms | 9.5 ms |
| + 50 ms `await` (slow database) | 972 | 51 ms | 56 ms | 2.8 ms |
| + 5 ms synchronous CPU block | 189 | 260 ms | 512 ms | 252 ms |
| `/api/attendance` (PBL endpoint) | 5,917 | 7 ms | 16 ms | 11.9 ms |

FastAPI (one uvicorn worker, 15 s): 50 ms `time.sleep` inside `async def` gave **18 req/s**; the same wait in a plain `def` gave **775 req/s**.

Findings that differ from the slides (all tested): the slide's percentile formula returns the maximum for p99 at 100 samples; `monitorEventLoopDelay` reports about the timer resolution even when idle, so the resolution must be subtracted; `/metrics` and autocannon p99 are not "close" (they measure different spans) and `/metrics` only covers the last 1,000 requests.
Not done: the optional profiler packages (`bodhi-node-profiler`, `fastapi-profiler-lite`, and so on) were not installed or tested, and the k6 script was written but not run.

### P-4: Presentation (Lecture 59)
No coding task. Provided a guide with the required content checklist and timing, a fill-in outline template, the peer-review rubric, and a worked example on event-driven serverless with a rendered diagram, trade-off table, three Q&As and annotated references (two web pages read and cited). **Your topic, slides and real contributions are yours to write**, and the example's real-world slide is intentionally left for you to source.

## 3. How to run
```bash
cd "unit-5(P-1)"; npm install; npm test; npm run demo
cd "../unit-5(P-2)"; npm install; npm test; npm run invoke:local
cd "../unit-5(P-3)"; npm install; npm test; npm run experiment
cd fastapi-app; pip install -r requirements.txt; python -m pytest -q
```
Quote folder names in the terminal because of the brackets.

## 4. Limitations and honest notes
- **No real RabbitMQ, Consul, AWS or Docker** were available. P-1 and P-2 are verified against in-repo stand-ins; real-service runs, the AWS deployment and screenshots are yours to do (see each README).
- **Timings** come from a shared 2 vCPU sandbox where the load generator competes with the server; compare scenarios with each other, and rerun on your machine for your report.
- The worked P-3 bottleneck was **introduced deliberately**, as Task 3 asks; your report needs your own endpoint and numbers.
- References: only the AWS pages I fetched are cited; read and re-check every link before you use it.

## 5. To finish before submission
- [ ] Add your name and SAP ID
- [ ] P-1: run the demo with real RabbitMQ and Consul (Docker) and screenshot the duplicate test and the health-check disappearance
- [ ] P-2: deploy with SAM, inspect the IAM role, send the duplicate message, screenshot DynamoDB and CloudWatch, then `sam delete`
- [ ] P-3: run the load test on your machine and fill the report template with your numbers
- [ ] P-4: build your topic's slides and rehearse; complete the contribution table
- [ ] `git add . && git commit -m "Unit 5 practicals" && git push`

## Sources
Unit 5 lecture slides (Dr. Prateek Raj Gautam), as supplied in the HTML exports. AWS Lambda Developer Guide pages cited in `unit-5(P-4)/examples/event-driven-serverless/REFERENCES.md`.
