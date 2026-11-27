// Static checks of the infrastructure files: least privilege, queue settings, anti-pattern guard.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = (p) => readFileSync(new URL(`../${p}`, import.meta.url), 'utf8');
const template = read('template.yaml');
const code = template.split('\n').filter((l) => !l.trim().startsWith('#')).join('\n');   // ignore comments

test('the function policy allows exactly one action: dynamodb:PutItem', () => {
  const actions = [...template.matchAll(/Action:\s*(\S+)/g)].map((m) => m[1]);
  assert.deepEqual(actions, ['dynamodb:PutItem']);
});

test('no wildcard actions or resources anywhere', () => {
  assert.doesNotMatch(template, /Action:\s*['"]?\*/);
  assert.doesNotMatch(template, /dynamodb:\*/);
  assert.doesNotMatch(template, /Resource:\s*['"]?\*/);
  const policy = JSON.parse(read('iam/function-policy.json'));
  for (const s of policy.Statement) {
    assert.notEqual(s.Action, '*'); assert.notEqual(s.Resource, '*');
    assert.equal(s.Action, 'dynamodb:PutItem');
  }
});

test('the policy is scoped to the audit table ARN, not to every table', () => {
  assert.match(template, /Resource:\s*!GetAtt AuditTable\.Arn/);
});

test('the broader SAM policy template is not used', () => {
  assert.doesNotMatch(code, /DynamoDBCrudPolicy|DynamoDBWritePolicy|AWSLambdaFullAccess|AdministratorAccess/);
});

test('trust policy names only lambda.amazonaws.com', () => {
  const trust = JSON.parse(read('iam/trust-policy.json'));
  assert.equal(trust.Statement[0].Principal.Service, 'lambda.amazonaws.com');
  assert.equal(trust.Statement[0].Action, 'sts:AssumeRole');
});

test('partial batch responses are switched on for the SQS event source', () => {
  assert.match(template, /FunctionResponseTypes:\s*\[ReportBatchItemFailures\]/);
});

test('function timeout is shorter than the queue visibility timeout', () => {
  const timeout = Number(/Timeout:\s*(\d+)/.exec(template)[1]);
  const visibility = Number(/VisibilityTimeout:\s*(\d+)/.exec(template)[1]);
  assert.ok(timeout < visibility, `${timeout} should be < ${visibility}`);
  assert.ok(visibility >= 6 * timeout, '6 x the function timeout is the guidance I followed; verify it in the AWS docs');
});

test('a dead-letter queue is configured with a receive limit', () => {
  assert.match(template, /deadLetterTargetArn:\s*!GetAtt SmsEventsDLQ\.Arn/);
  assert.match(template, /maxReceiveCount:\s*\d+/);
});

test('the table key is eventId (the idempotency key)', () => {
  assert.match(template, /AttributeName:\s*eventId\s*\n\s*KeyType:\s*HASH/);
});

test('table name reaches the function through an environment variable, not code', () => {
  assert.match(template, /AUDIT_TABLE:\s*!Ref AuditTable/);
  assert.doesNotMatch(read('src/index.mjs'), /TableName:\s*['"]/);
});

test('anti-pattern guard (recursion): the function never writes to the queue that triggers it', () => {
  // it imports no SQS client and the policy has no sqs:SendMessage
  assert.doesNotMatch(read('src/index.mjs'), /client-sqs|SendMessage/);
  assert.doesNotMatch(template, /sqs:SendMessage/);
});

test('anti-pattern guard (synchronous waits): one write per event, no chained calls', () => {
  const src = read('src/index.mjs');
  assert.equal((src.match(/client\.send\(/g) ?? []).length, 1);
});

test('no AWS keys in any project file', () => {
  for (const f of ['template.yaml', 'src/index.mjs', 'events/event.json', 'iam/function-policy.json', 'package.json']) {
    assert.doesNotMatch(read(f), /AKIA[0-9A-Z]{16}/, f);
  }
});
