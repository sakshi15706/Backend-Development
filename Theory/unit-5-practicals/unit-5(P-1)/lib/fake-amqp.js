'use strict';
/**
 * A tiny in-memory stand-in for the parts of `amqplib` used in this practical:
 *   connect -> createChannel -> assertQueue / prefetch / sendToQueue / consume / ack / nack / close
 *
 * WHY IT EXISTS: the lab environment used to prepare this folder had no RabbitMQ and no Docker.
 * The fake lets the tests and demo.js run anywhere, and it implements the behaviours that
 * matter for idempotency: unacked messages are redelivered, nack(requeue=true) puts the
 * message back, prefetch limits how many unacked messages a consumer holds.
 * It is NOT RabbitMQ: no exchanges, routing, persistence, clustering or network failures.
 */
class FakeBroker {
  constructor() {
    this.queues = new Map();      // name -> { ready: [], consumers: [], unacked: Set }
    this.deliveryCounter = 0;
    this.stats = { published: 0, delivered: 0, acked: 0, nacked: 0, redelivered: 0 };
  }

  queue(name) {
    if (!this.queues.has(name)) this.queues.set(name, { ready: [], consumers: [], unacked: new Set() });
    return this.queues.get(name);
  }

  /** the object to pass wherever the code expects the `amqplib` module */
  amqp() {
    const broker = this;
    return {
      async connect() {
        const channels = [];
        return {
          async createChannel() { const ch = new FakeChannel(broker); channels.push(ch); return ch; },
          async close() { for (const ch of channels) await ch.close(); },
        };
      },
    };
  }

  /** resolves when nothing is waiting or in flight (handy in tests) */
  async drain(timeoutMs = 2000) {
    const start = Date.now();
    for (;;) {
      await new Promise((r) => setImmediate(r));
      const busy = [...this.queues.values()].some(
        (q) => (q.consumers.length > 0 && q.ready.length > 0) || q.unacked.size > 0);
      if (!busy) return;
      if (Date.now() - start > timeoutMs) throw new Error('FakeBroker.drain timed out');
      await new Promise((r) => setTimeout(r, 1));
    }
  }

  pump(name) {
    const q = this.queue(name);
    for (const consumer of q.consumers) {
      while (q.ready.length > 0 && consumer.channel.open && consumer.inFlight < consumer.channel.prefetchCount) {
        const msg = q.ready.shift();
        consumer.inFlight += 1;
        q.unacked.add(msg);
        msg.consumer = consumer;
        this.stats.delivered += 1;
        if (msg.fields.redelivered) this.stats.redelivered += 1;
        setImmediate(() => Promise.resolve(consumer.callback(msg)).catch(() => {}));
      }
    }
  }
}

class FakeChannel {
  constructor(broker) { this.broker = broker; this.open = true; this.prefetchCount = Infinity; this.consumers = []; }
  async assertQueue(name) { this.broker.queue(name); return { queue: name }; }
  prefetch(n) { this.prefetchCount = n > 0 ? n : Infinity; }
  sendToQueue(name, content, options = {}) {
    if (!Buffer.isBuffer(content)) throw new TypeError('content must be a Buffer');
    const q = this.broker.queue(name);
    this.broker.deliveryCounter += 1;
    this.broker.stats.published += 1;
    q.ready.push({ content, properties: options, fields: { redelivered: false, deliveryTag: this.broker.deliveryCounter, routingKey: name }, queueName: name });
    this.broker.pump(name);
    return true;
  }
  async consume(name, callback) {
    const consumer = { channel: this, callback, inFlight: 0, queueName: name };
    this.broker.queue(name).consumers.push(consumer);
    this.consumers.push(consumer);
    this.broker.pump(name);
    return { consumerTag: `ctag-${this.consumers.length}` };
  }
  _settle(msg) {
    const q = this.broker.queue(msg.queueName);
    if (!q.unacked.delete(msg)) return false;       // already settled
    msg.consumer.inFlight -= 1;
    return true;
  }
  ack(msg) {
    if (this._settle(msg)) this.broker.stats.acked += 1;
    this.broker.pump(msg.queueName);
  }
  nack(msg, allUpTo = false, requeue = true) {
    if (this._settle(msg)) {
      this.broker.stats.nacked += 1;
      if (requeue) {
        msg.fields.redelivered = true;
        this.broker.queue(msg.queueName).ready.unshift(msg);
      }
    }
    this.broker.pump(msg.queueName);
  }
  async close() {
    if (!this.open) return;
    this.open = false;
    for (const consumer of this.consumers) {          // unacked messages go back to the queue
      const q = this.broker.queue(consumer.queueName);
      for (const msg of [...q.unacked]) if (msg.consumer === consumer) {
        q.unacked.delete(msg); msg.fields.redelivered = true; q.ready.unshift(msg);
      }
      q.consumers = q.consumers.filter((c) => c !== consumer);
    }
  }
}

module.exports = { FakeBroker };
