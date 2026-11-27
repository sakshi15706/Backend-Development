# Unit 5 (P-1): Service Discovery, Inter-Service Communication and Serverless (Lectures 52-54)

**PBL:** extend the SMS microservices: register Attendance and Notification in a registry, connect them with a broker (`attendance.marked` to notification), migrate one job to a serverless function, and present the architecture.

## Quick start (no Docker needed)
```bash
cd "unit-5(P-1)"
npm install
npm test          # 45 tests
npm run demo      # the whole flow, narrated, using in-repo stand-ins for Consul and RabbitMQ
```

## Two modes: stand-ins or the real thing
This folder was built in an environment with no Docker, RabbitMQ or Consul, so everything runs **against stand-ins** by default:

| Real service | Stand-in in this folder | Notes |
|---|---|---|
| Consul agent | `registry/mock-consul.js` | implements only the HTTP calls used here and runs real HTTP health checks |
| RabbitMQ (`amqplib`) | `lib/fake-amqp.js` | queues, ack/nack, redelivery, prefetch. No exchanges, no network failures |

The application code (`consul-client.js`, `producer.js`, `consumer.js`, `bridge.js`, the function) is the same code that talks to the real services. **I have not run it against a real RabbitMQ or Consul**, so do that for your demonstration:
```bash
docker run -d --name sms-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
docker run -d --name sms-consul -p 8500:8500 consul agent -dev -client=0.0.0.0
curl -s http://localhost:8500/v1/status/leader && echo " <- consul up"

# terminal 1: Notification consumer          terminal 2: Attendance service (registers itself in Consul)
node broker/consumer.js                      CONSUL_URL=http://localhost:8500 node services/attendance-service.js
# terminal 3
curl -X POST localhost:4001/attendance -d '{"eventId":"evt-0001","studentId":"S102","classId":"class-5A","present":true}'
curl -X POST localhost:4001/attendance -d '{"eventId":"evt-0001","studentId":"S102","classId":"class-5A","present":true}'
node registry/discover.js
```
The Consul image name may have changed (HashiCorp now publishes `hashicorp/consul`); check Docker Hub if `consul` does not pull. Environment variables: `AMQP_URL` (default `amqp://localhost`), `CONSUL_URL` (default `http://localhost:8500`).

## Slide task to file
| Slide task | Files |
|---|---|
| Task 1: register in Consul, discover healthy instances | `registry/consul-client.js`, `registry/discover.js`, `services/attendance-service.js` (`/health`, `/health/fail`, `/health/recover`) |
| Task 1 checkpoint: stop `/health`, instance disappears | `test/registry.test.js`, `npm run demo` |
| Task 2: producer | `broker/producer.js` (durable queue, persistent messages, validates the event) |
| Task 2: idempotent consumer | `broker/consumer.js`, `broker/idempotency.js` |
| Task 2 checkpoint: same `eventId` twice, one notification | `test/broker.test.js`, `test/e2e.test.js` |
| Task 3: serverless function | `serverless/index.js` (`sendAttendanceEmail`), `serverless/bridge.js` |
| PBL Classify and Migrate, Review | `docs/ARCHITECTURE.md` |

Run the function with the real Functions Framework: `npm run function` (port 8080), then `curl -X POST localhost:8080 -H 'content-type: application/json' -d '{"type":"attendance.marked","eventId":"e1","studentId":"S1","classId":"c","present":true}'`.

## Differences from the slide code, and why
- **Idempotency order.** The slide records the `eventId` *before* handling. If the handler then fails, the redelivered message is skipped as a "duplicate" and the notification is lost. Here the id is stored **after** success, and a failure nacks with requeue. `test/broker.test.js` contains a test that shows the slide order losing an event.
- **Poison messages.** Invalid JSON or a missing `eventId` is rejected without requeue, so it cannot loop forever. A real system adds a retry limit and a dead-letter queue.
- **In-flight duplicates.** With `prefetch > 1` two copies of one event can be in flight at once; the second is put back and dropped as a duplicate once the first finishes.
- **Persistent store option.** `FileStore` survives a restart. In production use a database table with a unique key on `eventId` (see unit-5(P-2) for the DynamoDB version).
- **No `node-fetch`.** Node 18+ has `fetch` built in.
- **The mail host** `api.mail-mock.local` in the slide does not exist, so the function does a **dry run** (logs the e-mail) unless `MAIL_API_URL` is set.
- The function never keeps state; it answers 502 when the mail provider fails, so the bridge retries.

## Checkpoint answers (for the viva)
1. *Why does the instance vanish from `passing=true`?* Consul probes `/health` every `Interval`. A non-2xx answer or a timeout marks the check **critical**, and `?passing=true` returns only instances with all checks passing. Clients therefore stop sending traffic to a broken instance without anybody editing a config file.
2. *Why is the idempotency guard needed?* At-least-once delivery means the broker redelivers when an ack is lost or a consumer dies after processing but before acking, so the same event can arrive twice. The consumer must make processing the same `eventId` twice harmless.
3. *Why can the function not keep a DB connection or WebSocket, and why must Notification stay long-lived?* A function instance can be frozen or destroyed between invocations and many run in parallel, so nothing in memory or open connections can be relied on. The push service holds WebSocket connections open for hours, which needs a process that stays alive.

## Evaluation mapping
| Criterion | Evidence |
|---|---|
| Conceptual understanding | checkpoint answers above, `docs/ARCHITECTURE.md` |
| Practical skill | registration with health check, producer plus idempotent consumer, function responding to an event (all tested) |
| Problem solving | sync/async classification and serverless choice in `docs/ARCHITECTURE.md` |
| CO5 team review | review questions and answers in `docs/ARCHITECTURE.md`; each member explains one decision |
