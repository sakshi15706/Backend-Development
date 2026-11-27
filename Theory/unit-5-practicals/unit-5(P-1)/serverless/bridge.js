'use strict';
/**
 * The "thin bridge" in the Notification service: forwards sms.events messages to the function's
 * HTTP endpoint. In production a managed trigger (Eventarc, SQS->Lambda, ...) does this for you.
 *
 * A message is acknowledged only when the function answers 2xx. Any other answer or a network
 * error makes the consumer nack(requeue) so the broker retries. The idempotency store means
 * that an event the function already handled successfully is not e-mailed twice.
 */
const { startConsumer } = require('../broker/consumer');

async function startBridge({ channel, functionUrl, store, fetchImpl = fetch, logger = console, queue, prefetch = 10 }) {
  const handler = async (event) => {
    const response = await fetchImpl(functionUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(event),
      signal: AbortSignal.timeout(10000),
    });
    if (!response.ok) throw new Error(`function answered ${response.status}`);
  };
  return startConsumer({ channel, handler, store, logger, queue, prefetch });
}

module.exports = { startBridge };
