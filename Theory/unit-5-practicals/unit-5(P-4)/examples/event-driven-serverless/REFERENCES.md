# Annotated references for the worked example

A reference earns its place only if it changed or supports a claim, and you say how. Two rules: **read it before you cite it**, and write the annotation yourself.

| Reference | What I used it for | Checked |
|---|---|---|
| Lecture 52-54 and 55-57 slides (Dr. Prateek Raj Gautam, SlideGen): Service Discovery, Messaging and Serverless; Serverless Backends with AWS Lambda | the SMS scenario, sync vs async table, idempotency requirement, the SQS to Lambda to DynamoDB topology | read in full |
| AWS Lambda Developer Guide, "Handling errors for an SQS event source in Lambda" (https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-errorhandling.html) | confirmed that `ReportBatchItemFailures` must be enabled, that only the returned message IDs reappear, and that an empty `batchItemFailures` means full success; this is why the handler returns partial failures instead of throwing | fetched and read on 2026-11-24; the page did not state the visibility-timeout ratio or DLQ setup, so I did not cite it for those |
| AWS Lambda Developer Guide, "Lambda runtimes" (https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html) | chose `nodejs22.x`: `nodejs20.x` was no longer in the supported table | fetched 2026-11-24; dates are forecasts and can change |
| This repository: `unit-5(P-2)` (tests, template) | all code claims on slides 5 to 8 | I ran `npm test`: 32 passing (an in-memory DynamoDB, not real AWS) |

Do **not** cite: pages you only saw in a search result, blogs you did not open, or benchmarks you cannot reproduce.
