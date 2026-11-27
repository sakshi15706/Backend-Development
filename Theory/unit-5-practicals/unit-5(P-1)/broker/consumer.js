'use strict';
/**
 * Task 2, consumer with an idempotency guard.
 *
 * Differences from the slide's version (and why):
 *  1. The eventId is remembered only AFTER the handler succeeded. The slide adds it first, so a
 *     failure after that point would leave an event that is "seen" but never processed, and the
 *     redelivery would be silently dropped (a lost notification).
 *  2. A failing handler -> nack with requeue, so the broker redelivers. (A real system adds a
 *     retry limit and a dead-letter queue so a poison message cannot loop forever.)
 *  3. Messages that can never succeed (invalid JSON, no eventId) are rejected WITHOUT requeue.
 *  4. Two copies of the same event can be in flight at once when prefetch > 1; the second is
 *     put back and will be dropped as a duplicate once the first one has finished.
 */
const { MemoryStore } = require('./idempotency');
const { DEFAULT_QUEUE } = require('./producer');

async function startConsumer({
  channel, queue = DEFAULT_QUEUE, handler, store = new MemoryStore(), prefetch = 10, logger = console,
}) {
  const inFlight = new Set();
  await channel.assertQueue(queue, { durable: true });
  channel.prefetch(prefetch);

  await channel.consume(queue, async (msg) => {
    if (!msg) return;                                   // consumer cancelled by the broker

    let event;
    try {
      event = JSON.parse(msg.content.toString());
    } catch {
      logger.error('rejecting message: invalid JSON');
      return channel.nack(msg, false, false);
    }
    if (!event || !event.eventId) {
      logger.error('rejecting message: no eventId');
      return channel.nack(msg, false, false);
    }

    if (await store.has(event.eventId)) {               // already processed: acknowledge and skip
      logger.info(`duplicate ${event.eventId} skipped`);
      return channel.ack(msg);
    }
    if (inFlight.has(event.eventId)) {                  // same event is being processed right now
      return channel.nack(msg, false, true);
    }

    inFlight.add(event.eventId);
    try {
      await handler(event);
      await store.add(event.eventId);                   // remember only after success
      channel.ack(msg);
    } catch (err) {
      logger.error(`handler failed for ${event.eventId}: ${err.message}; requeueing`);
      channel.nack(msg, false, true);
    } finally {
      inFlight.delete(event.eventId);
    }
  });
}

/** the "notification": a console line, exactly as in the slide */
function notifyHandler(event, out = console) {
  out.log('notify:', event.studentId, 'was', event.present ? 'present' : 'absent');
}

module.exports = { startConsumer, notifyHandler };

// node broker/consumer.js   -> the Notification service consumer (needs RabbitMQ running)
if (require.main === module) {
  const amqp = require('amqplib');
  (async () => {
    const conn = await amqp.connect(process.env.AMQP_URL || 'amqp://localhost');
    const channel = await conn.createChannel();
    await startConsumer({ channel, handler: (e) => notifyHandler(e) });
    console.log('Notification consumer waiting for events on', DEFAULT_QUEUE);
  })().catch((e) => { console.error(e.message); process.exit(1); });
}
