# Assignment III: presentation architecture and evidence (Lecture 59)

**Task:** turn your assigned advanced backend topic into a 15-minute presentation: **8 to 12 slides**, built as an argument, not a list of definitions.

## 1. The blueprint (slide order)
problem, then concept, then architecture/flow, then implementation choices, then a real-world use case, then limitations and trade-offs, then conclusion, then questions.

## 2. Required content (checklist from the lecture)
- [ ] 8 to 12 slides, deliverable in 15 minutes
- [ ] **One main diagram** that explains a flow, a boundary or a decision (not decoration)
- [ ] **One comparison or trade-off slide**
- [ ] **One real-world example** (cite where it comes from)
- [ ] **Two to four questions with answers**
- [ ] **Contribution details** (who did what)
- [ ] **Annotated references** (what each gave you, not just a link)

## 3. Plan the 15 minutes
| Block | Slides | Minutes |
|---|---|---|
| Problem and why it matters | 1 to 2 | 2 to 3 |
| Concept and architecture/flow (main diagram) | 3 to 5 | 4 to 5 |
| Implementation choices, evidence | 6 to 7 | 3 |
| Real-world example, limitations, trade-offs | 8 to 10 | 3 |
| Conclusion, questions | 11 to 12 | 1 to 2 |
Leave 30 seconds of slack. Rehearse with a timer; peer reviewers score timing.

## 4. Topic hints and where to find evidence in this course
| Topic | What the slides should show | Evidence you could cite |
|---|---|---|
| WebSockets | handshake, persistent channel, message lifecycle | Unit 4 practicals (not part of Unit 5 files) |
| Socket.io | events, rooms, broadcasting, versus raw WebSocket | Unit 4 practicals |
| Microservices | decomposition, benefits, operational cost | Unit 4 practicals, `unit-5(P-1)/docs/ARCHITECTURE.md` |
| Discovery | registration, health checks, dynamic routing | `unit-5(P-1)`: Consul client, health failure removes the instance, tested |
| REST between services | gateway, sequence diagram, timeouts and retries | `unit-5(P-1)/docs/ARCHITECTURE.md` section 3 (sync vs async table) |
| Messaging | producer, broker, consumer, delivery and consistency | `unit-5(P-1)`: idempotent consumer, redelivery tests |
| Serverless | trigger, function, limits, cost, cold start | `unit-5(P-1)/serverless`, `unit-5(P-2)/docs/CLASSIFICATION.md` |
| Cloud functions | handler, configuration, permissions, logs | `unit-5(P-2)/src/index.mjs`, `template.yaml` |
| Event-driven serverless | event bus, queue, retry, dead-letter path | `unit-5(P-2)`: batch failures, DLQ; worked example in `examples/` |
| Profiling | baseline, measurement, bottleneck, improvement evidence | `unit-5(P-3)`: `results/`, `PROFILING_REPORT.md` |

## 5. How to build each element well
**Main diagram.** Number the arrows in the order they happen; label each arrow with what travels on it; mark the boundary (what is inside the service, what is managed); show at least one failure path. If you cannot explain every arrow in ten seconds, remove it. Check the diagram against your code or documentation before the review: *diagram accuracy* is scored.

**Trade-off slide.** Two or three options, three or four criteria that matter for your case, and a decision with the reason. "It depends" is not a conclusion.

**Real-world example.** A named, real system you have read about. Say what it does with the technique and cite the source. Do not invent company details or numbers; if you cannot find a source, use your own project as the example and say so.

**Questions and answers.** Questions the audience will really ask (why not the alternative? what breaks first? what does it cost?), answers of two or three sentences.

**Annotated references.** Read each source before you cite it. Write one or two sentences: what claim it supports, what you learned that you did not know. Prefer official documentation and primary sources; discuss the references in the talk instead of listing them on the last slide.

**Evidence.** Claims about performance, behaviour or cost need a number, a test, or a source. Say where the evidence is (a test name, a results file, a link).

## 6. Rehearsal checklist
- [ ] Timed run under 15 minutes with every member speaking
- [ ] Each slide has one claim you can say in one sentence
- [ ] Diagram readable from the back of the room (large text, few boxes)
- [ ] Every number has a source or a test behind it
- [ ] Each member can answer questions on the whole talk, not only their slides
- [ ] Backup: slides exported to PDF

## 7. Deliverables in this folder
| File | Use |
|---|---|
| `templates/slide-outline-template.md` | fill in for your topic |
| `examples/event-driven-serverless/` | complete worked example: outline, diagram (`.mmd`, `.svg`, `.png`), Q&A, annotated references |
| `PEER_REVIEW_RUBRIC.md` | score a classmate's draft slides |
