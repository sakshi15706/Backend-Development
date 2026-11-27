# Worked example: Event-driven serverless for the SMS (12 slides, 15 minutes)

This is a **model to learn from**, not a presentation to submit: the content comes from the practicals in this repository (`unit-5(P-1)` and `unit-5(P-2)`). Your assigned topic and your own evidence will differ. Notice how each slide makes a claim and how the evidence behind it can be checked.

**Argument (one sentence):** *Put an SQS queue between the fast producer and a Lambda consumer, and make the write idempotent, so that retries, duplicates and bad messages cannot corrupt the data or loop forever.*

| # | Slide | Time | Content | Evidence in the repo |
|---|---|---|---|---|
| 1 | Title + problem | 1:00 | Results day: thousands of events in minutes; a 24/7 e-mail server for a yearly spike is wasteful; the Attendance service must not wait for slow consumers | scenario in the lecture PBL |
| 2 | Core concepts | 1:30 | event, queue, function, at-least-once delivery, idempotency (one line each) | `unit-5(P-1)/docs/ARCHITECTURE.md` |
| 3 | **Main diagram** | 2:00 | `architecture.png`: numbered flow 1 to 6. Walk the happy path first, then the two failure paths | `architecture.mmd` |
| 4 | Event contract | 1:00 | `{eventId, type, studentId, classId, present, at}`; `eventId` is the idempotency key | `unit-5(P-2)/events/event.json` |
| 5 | Idempotent write | 1:30 | `ConditionExpression: attribute_not_exists(eventId)`. A duplicate raises `ConditionalCheckFailedException`, which the handler treats as success | `src/index.mjs`, test "same event twice leaves exactly one item" |
| 6 | Retries and the DLQ | 1:30 | partial batch response, `maxReceiveCount: 3`, dead-letter queue, poison messages | `template.yaml`, `events/batch-mixed.json` |
| 7 | **Trade-off / comparison** | 1:30 | Lambda vs always-on container for this workload (table below) | `unit-5(P-2)/docs/CLASSIFICATION.md` |
| 8 | Least privilege | 1:00 | role has ONE action on ONE table; removing it gives `AccessDeniedException`, the correct failure | `template.yaml`, `test/template.test.mjs` |
| 9 | **Real-world example** | 1:00 | an e-commerce order or notification pipeline buffering bursts through a queue into functions *(use a source you have actually read; see the reference rules)* | your reference |
| 10 | Limitations | 1:00 | dual-write gap (outbox pattern), cold starts, vendor lock-in, no real AWS deployment in my evidence | honest limits list |
| 11 | Quick Q&A | 1:00 | three questions with answers (below) | |
| 12 | Conclusion + contributions | 0:30 | one-sentence takeaway; who did what | contribution table |
| | **Total** | **14:30** | 30 s of slack | |

## Comparison slide (slide 7)
| | Lambda + SQS | Always-on container |
|---|---|---|
| Idle cost | about zero | pays for uptime |
| Burst handling | scales out automatically | needs autoscaling rules |
| Persistent connections (WebSocket, DB pool) | not possible across invocations | natural |
| Cold start | possible, fine for async work | none |
| Steady high traffic | can cost more | can cost less |
| **Our decision** | e-mail dispatch (bursty, stateless) | WebSocket Notification service |

## Questions and answers (slide 11)
1. **Why can a duplicate message arrive at all?** At-least-once delivery: if a consumer finishes but its acknowledgement/delete is lost, or a timeout expires first, the queue delivers the message again. Hence idempotency by `eventId`.
2. **Why is a duplicate not an error in the handler?** The condition failing means the work is already done. Treating it as an error would send the record back to the queue and eventually to the DLQ for no reason (the lecture's sample code does not handle this).
3. **What if the function is too slow for the visibility timeout?** The message becomes visible again while still being processed, so a second copy is delivered. The function timeout must be shorter than the visibility timeout, and the idempotent write makes the overlap harmless.

## Contribution details (fill in for a team)
| Member | Slides / parts | Evidence of contribution |
|---|---|---|
| | | |

## Speaker notes pattern
Per slide: **claim** (the sentence the audience should remember), **show** (diagram or table), **say** (30 seconds), **prove** (where the evidence is).
