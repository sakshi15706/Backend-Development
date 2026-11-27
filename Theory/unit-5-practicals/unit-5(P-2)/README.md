# Unit 5 (P-2): Building Serverless Backends with AWS Lambda (Lectures 55-57)

**PBL:** deploy an `attendance.marked` / `result.published` consumer as a Lambda function behind SQS, with a least-privilege execution role and a DynamoDB idempotency table; audit the topology for recursion and synchronous waits; classify components as SaaS/PaaS/FaaS.

## What is verified and what is not
| Part | Status |
|---|---|
| Handler logic (idempotency, partial batch response, DLQ behaviour, timeouts) | **tested** with an in-memory DynamoDB: 32 tests |
| `template.yaml` (SAM) | `cfn-lint` clean; checked by static tests (single IAM action, scoped ARN, DLQ, timeouts) |
| Real deployment, IAM role in the console, SQS trigger, DynamoDB items | **not run: needs your AWS account.** Steps in `docs/DEPLOY_AWS.md` |
| `sam local invoke` | **not run** (needs Docker). `npm run invoke:local` is a stand-in for the handler logic only |

## Quick start
```bash
cd "unit-5(P-2)"
npm install
npm test                  # 32 tests
npm run invoke:local      # runs events/event.json twice: 1 item stored, second run = duplicate skipped
node scripts/invoke-local.mjs events/batch-mixed.json   # duplicate + poison + unknown type in one batch
```
Requires Node 18+ (tested on 22).

## Files
| File | Purpose |
|---|---|
| `src/index.mjs` | the Lambda handler (`index.handler`) |
| `template.yaml` | SAM: queue, DLQ, table, function, scoped policy, SQS event source |
| `iam/trust-policy.json`, `iam/function-policy.json` | the trust policy (lambda.amazonaws.com) and the one-action policy, for reference |
| `events/event.json` | the slide's sample SQS event; `batch-mixed.json` shows duplicate, poison and unknown records |
| `test/` , `test-support/` | tests and the in-memory DynamoDB |
| `docs/DEPLOY_AWS.md` | deploy, verify, clean up |
| `docs/ANTIPATTERN_AUDIT.md` | recursion and synchronous-wait audit with fixes |
| `docs/CLASSIFICATION.md` | SaaS / PaaS / FaaS table for the SMS |

## Differences from the slide, and why (good viva material)
1. **Duplicate = success.** `attribute_not_exists(eventId)` makes DynamoDB *throw* `ConditionalCheckFailedException` on a duplicate. The slide's handler does not catch it, so a duplicate would fail the whole batch and the messages would cycle back to the queue. The handler treats that exception as "already processed".
2. **Partial batch response.** Only failed records are returned in `batchItemFailures`, and the event source enables `ReportBatchItemFailures`. Without it, one failure would retry the whole batch, and the successful records would be re-run.
3. **Poison messages** fail and go to the DLQ rather than being dropped silently or retried forever (`maxReceiveCount: 3`).
4. **Time guard:** below one second remaining the handler hands back the unprocessed records for retry.
5. **Runtime** `nodejs22.x` instead of the slide's `nodejs20.x`. When I checked the AWS runtimes page (Nov 2026), `nodejs20.x` was no longer in the supported table, while `nodejs22.x` was (listed with a May 2027 deprecation date, which can change). Check the page again before you deploy.
6. **Scoped policy:** one action, one table ARN, as the slide's Task 2 asks.
7. Records of both `attendance.marked` (Task 1) and `result.published` (PBL) are stored.

## Checkpoint answers
- **What does `ConditionExpression: attribute_not_exists(eventId)` do and why does it give idempotency?** The write succeeds only if no item with that key exists, atomically in DynamoDB. A redelivered event finds the key and is rejected, so each `eventId` is stored once even though SQS delivers at least once.
- **Why is the `AccessDeniedException` a correct failure?** The role contains only what was granted. Removing `PutItem` shows that the function cannot do anything else either, so a compromised function cannot read or delete the student data.
- **Event and context:** `event` is the trigger's payload (here `Records[]` from SQS); `context` has invocation metadata (`awsRequestId`, `getRemainingTimeInMillis()`).
- **Sync vs async vs poll-based:** API Gateway calls Lambda synchronously (caller waits), S3/SNS invoke it asynchronously (Lambda retries twice and can use a DLQ), SQS is polled by Lambda in batches (partial batch failures supported). This function is poll-based.
- **Topology labels:** producer (any service), SQS (managed service), Lambda (FaaS), DynamoDB (managed service); the idempotency guard lives in DynamoDB, enforced by the condition on the write.

## Known limits
- The handler stores a minimal audit record; a real e-mail function would call SES (SaaS) after the idempotent write, and would need care to avoid sending twice if the e-mail succeeds but the write fails (write a "pending" record first, or use SES message de-duplication ideas).
- No reserved concurrency, alarms or X-Ray tracing are configured.
- Item TTL is not set; add a `ttl` attribute if the table should expire old events.
