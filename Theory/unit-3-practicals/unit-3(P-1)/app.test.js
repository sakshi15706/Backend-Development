// Run with:  npm test
const test = require('node:test');
const assert = require('node:assert');
const app = require('./app');

let server;
let base;

test.before(async () => {
  await new Promise((resolve) => {
    server = app.listen(0, () => {          // port 0 = any free port
      base = `http://127.0.0.1:${server.address().port}`;
      resolve();
    });
  });
});

test.after(() => server.close());

test('GET / responds 200 with "API is running"', async () => {
  const res = await fetch(`${base}/`);
  assert.strictEqual(res.status, 200);
  assert.strictEqual(await res.text(), 'API is running');
});

test('unknown route gives 404', async () => {
  const res = await fetch(`${base}/nope`);
  assert.strictEqual(res.status, 404);
});

test('JSON body parsing middleware is active', async () => {
  // No POST route exists yet, so Express answers 404, but a malformed JSON body
  // must be rejected by express.json() with 400 before routing is reached.
  const res = await fetch(`${base}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: '{bad json'
  });
  assert.strictEqual(res.status, 400);
});
