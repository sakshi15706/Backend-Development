'use strict';
/** Task 2, producer: runs inside the Attendance service. */
const DEFAULT_QUEUE = 'sms.events';

function validateEvent(event) {
  const missing = ['eventId', 'type', 'studentId'].filter((k) => !event || !event[k]);
  if (missing.length) throw new Error(`event is missing: ${missing.join(', ')}`);
  if (event.type !== 'attendance.marked') throw new Error(`unsupported event type: ${event.type}`);
}

/**
 * Publish one event. A connection per call (as in the slide) is simple but slow; a real service
 * would keep one connection and channel open for its whole life.
 */
async function publishAttendanceMarked(event, {
  amqp = require('amqplib'),
  url = process.env.AMQP_URL || 'amqp://localhost',
  queue = DEFAULT_QUEUE,
} = {}) {
  validateEvent(event);
  const conn = await amqp.connect(url);
  try {
    const ch = await conn.createChannel();
    await ch.assertQueue(queue, { durable: true });                       // queue survives a broker restart
    ch.sendToQueue(queue, Buffer.from(JSON.stringify(event)), { persistent: true });   // message is written to disk
    await ch.close();
  } finally {
    await conn.close();
  }
  return event.eventId;
}

module.exports = { publishAttendanceMarked, validateEvent, DEFAULT_QUEUE };

// node broker/producer.js [eventId]   -> publishes one sample event (needs RabbitMQ running)
if (require.main === module) {
  publishAttendanceMarked({
    eventId: process.argv[2] || 'evt-0001', type: 'attendance.marked',
    classId: 'class-5A', studentId: 'S102', present: true, at: Date.now(),
  }).then((id) => console.log('published', id)).catch((e) => { console.error(e.message); process.exit(1); });
}
