# Anti-pattern audit (PBL task 2)

Two classic serverless anti-patterns (lecture §4): **recursion** and **synchronous waits**. The audit asks two questions of every function: *does it output to its own trigger?* and *could two functions replace one?*

## 1. Audit of this project's topology
```
producer --> SQS sms-events --> Lambda AttendanceConsumer --> DynamoDB AuditTable
                  |  (3 failed receives)
                  +--> SQS sms-events-dlq
```
| Check | Result | Evidence |
|---|---|---|
| Does the function write to the resource that triggers it? | **No.** It reads from SQS and writes to DynamoDB, which has no trigger. | `src/index.mjs` imports no SQS client; policy has no `sqs:SendMessage` (`test/template.test.mjs`) |
| Could the single function be split into two to avoid waiting? | **No need.** One write per event, nothing chained, so there is no wait to compound. | one `client.send` in the source (tested) |
| Can a failure loop forever? | **No.** `maxReceiveCount: 3` moves a repeatedly failing message to the DLQ. | `template.yaml` |
| Is a runaway scale-out possible? | Limited by SQS batching; for real protection set **reserved concurrency** on the function (not set here) | |

## 2. Worked bad examples and their fixes
### A. Recursive loop
```
S3 bucket "sms-receipts" --(ObjectCreated)--> Lambda --(PutObject: receipts/x.pdf)--> S3 bucket "sms-receipts"
```
Each output re-triggers the function, and both services scale automatically, so the loop can eat all available concurrency and your bill.
**Fixes:** write to a **different** bucket; or use a prefix filter on the trigger (`uploads/`) and write elsewhere (`receipts/`); put an SQS queue between steps; set reserved concurrency as a safety cap; add an invocation-count alarm. AWS also has built-in recursive-loop detection for some service combinations, but design so you never rely on it.

### B. Synchronous waits in one function
```
Lambda: put S3 (wait) -> put DynamoDB (wait) -> return        total = t1 + t2, billed the whole time
```
**Fix:** split in two. Lambda A writes to S3 and returns; the S3 event invokes Lambda B, which writes to DynamoDB. Each function bills only for its own part, and A responds sooner.
Trade-off to mention in the viva: splitting adds a trigger, a second function to deploy and monitor, and eventual consistency between the two steps. Do it when the waits are long or independent, not for a 5 ms call.

## 3. Audit table to fill for your own team's topology
| Function | Trigger | Outputs to | Outputs to trigger resource? | Sequential waits? | Fix |
|---|---|---|---|---|---|
| | | | | | |
