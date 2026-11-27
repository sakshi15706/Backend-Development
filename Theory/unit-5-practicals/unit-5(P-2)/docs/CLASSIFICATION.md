# SaaS, PaaS or FaaS? (PBL task 3)

Decide by **what you control** and **how you are billed**, not by marketing labels.

| Model | You control | Provider manages | Billing |
|---|---|---|---|
| SaaS | configuration and data only | everything | per seat / month |
| PaaS | application code, some runtime config | servers, OS, scaling, patching | per instance-hour, even idle |
| FaaS | individual stateless functions plus triggers | servers, runtime, scaling (to zero) | per invocation + duration |

| SMS component | Model | Justification |
|---|---|---|
| E-mail delivery provider (e.g. Amazon SES) | **SaaS** | we call an API; no code of ours runs there; billed per message |
| Node/Express Notification service with WebSockets | **PaaS-like (container)** | long-lived connections, always on, billed for uptime, needs persistent state |
| `AttendanceConsumer` Lambda | **FaaS** | stateless, event-triggered, bursty, billed per invocation |
| SQS queue | managed service (building block) | AWS runs it; we configure limits only |
| DynamoDB audit table | managed service (building block, on-demand billing) | no servers to manage |
| Moodle / Google Workspace used by the college | **SaaS** | configuration only |
| Main Student API on Render/Heroku | **PaaS** | we deploy code; provider runs the platform; per instance |

Boundary rule: if the workload needs persistent connections or warm in-memory state, or runs steadily at high load, prefer a container/PaaS. If it is bursty, event-driven and stateless, prefer FaaS. Cold starts matter little for asynchronous work.
