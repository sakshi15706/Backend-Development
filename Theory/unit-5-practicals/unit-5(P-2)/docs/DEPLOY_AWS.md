# Deploying to AWS (you must do this part)

**Status:** the handler logic, IAM policy shape and template were verified here (32 tests, `cfn-lint` clean). **Nothing was deployed or run against real AWS**: it needs your AWS account, credentials, and Docker for `sam local`. Follow these steps and take the screenshots your assessment asks for.

## Before you start
- Use a course IAM user (not the root account) with `aws configure`. **Never commit access keys.** Check `aws sts get-caller-identity`.
- Install the AWS SAM CLI and Docker (Docker only for `sam local invoke`).
- Runtime: the slide uses `nodejs20.x`, which was no longer in AWS's supported table when I checked (Nov 2026), so the template defaults to `nodejs22.x`. Check the Lambda runtimes page again and change the `LambdaRuntime` parameter if needed.
- Cost: Lambda's free tier (1M requests, 400,000 GB-seconds a month) and SQS/DynamoDB on-demand pricing make this lab effectively free at coursework volumes, but check current pricing and delete the stack when finished.

## Task 1: local invoke
```bash
npm install
npm run invoke:local                        # no Docker: in-memory stand-in, runs the event twice
sam build                                   # needs the AWS SDK: SAM bundles src/package.json dependencies
sam local invoke AttendanceConsumer --event events/event.json    # needs Docker and a table to write to
```
`sam local invoke` calls the real handler but a real DynamoDB table (set `AUDIT_TABLE` via `--env-vars`) or DynamoDB Local. Note: SAM builds from `CodeUri: src/`, so `src/package.json` lists the two AWS SDK packages and `"type": "module"` (needed for `index.mjs` imports). The Node.js Lambda runtime also bundles AWS SDK v3, but bundling your own pins the version.

## Task 2: deploy with the scoped role
```bash
sam build && sam deploy --guided           # accept the CAPABILITY_IAM prompt: the template creates a role
```
Inspect the function role in IAM: it should have `AWSLambdaBasicExecutionRole`, the SQS receive/delete permissions SAM adds for the event source, and our inline policy with `dynamodb:PutItem` on the audit table ARN.
**Checkpoint:** remove `dynamodb:PutItem`, redeploy, send a message. CloudWatch Logs show `AccessDeniedException` (the handler logs it as structured JSON), the message returns to the queue, and after 3 receives lands in `sms-events-dlq`. That is the correct failure for least privilege. (`test/handler.test.mjs` simulates the same.)

## Task 3: end-to-end
```bash
aws sqs send-message --queue-url <SmsEventsQueueUrl> \
  --message-body '{"eventId":"evt-1001","type":"attendance.marked","studentId":"S102","classId":"class-5A","present":true,"at":1730000000000}'
aws dynamodb scan --table-name <AuditTableName> --select COUNT      # expect 1
# send the same message again
aws dynamodb scan --table-name <AuditTableName> --select COUNT      # still 1
aws logs tail /aws/lambda/<ConsumerFunctionName> --since 10m        # "duplicate event skipped"
```
The stack outputs print the queue URL, table name and function name.

## Clean up
`sam delete` removes the stack (queues, table, function, role).

## Operational checklist (lecture §5.3) and where each item is
| Concern | Practice | Here |
|---|---|---|
| Least privilege | role scoped to one table, one action | `template.yaml`, tested |
| Idempotency | eventId written with `attribute_not_exists` before side effects | `src/index.mjs`, tested |
| Timeouts | function timeout shorter than queue visibility (guidance: about 6x) | 10 s vs 60 s, tested |
| Dead-letter queue | after 3 receives | `template.yaml` |
| Observability | structured JSON logs | `log()` in the handler |
| Cold starts | acceptable for async work | no provisioned concurrency |
| Secrets | none in code; keys only via `aws configure` or OIDC in CI | tested for key patterns |
