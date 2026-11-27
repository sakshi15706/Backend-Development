/**
 * npm run invoke:local [events/event.json]
 * Stand-in for `sam local invoke` (which needs Docker): calls the handler with an event file and an
 * in-memory DynamoDB. Runs the event TWICE, like the slide's checkpoint.
 * It proves the handler logic; it does NOT test IAM, the real SQS trigger or the real table.
 */
import { readFileSync } from 'node:fs';
import { createHandler } from '../src/index.mjs';
import { FakeDocClient } from '../test-support/fake-dynamodb.mjs';

const file = process.argv[2] ?? 'events/event.json';
const event = JSON.parse(readFileSync(file, 'utf8'));
const db = new FakeDocClient();
const handler = createHandler({ docClient: db, tableName: 'local-audit' });
const context = { awsRequestId: 'local-1', getRemainingTimeInMillis: () => 10000 };

for (const run of [1, 2]) {
  console.log(`\n--- run ${run} ---`);
  console.log('result:', JSON.stringify(await handler(event, context)));
  console.log('items in table:', db.items('local-audit').length);
}
