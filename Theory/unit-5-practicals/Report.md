# Backend Development Lab Report – Unit 5
## Advanced Topics

## 1. Introduction

Unit 5 focuses on advanced backend development concepts such as service discovery, message queues, event-driven architecture, serverless computing, AWS Lambda, cloud services, performance profiling, and application presentation.

The practicals helped in understanding how distributed backend applications communicate, how events are processed asynchronously, how serverless applications work, and how application performance can be measured and improved.

A total of four practicals were completed using Node.js, Express.js, FastAPI, RabbitMQ concepts, Consul, AWS services, and performance testing tools.

## 2. Practical Work and Concepts Covered

### Practical 1: Service Discovery, Messaging and Serverless Computing

**Objective:** To understand service discovery, asynchronous messaging, and serverless computing in distributed backend applications.

**Work Performed:**
- Implemented a service registry using Consul concepts.
- Registered services with HTTP health checks.
- Implemented service deregistration during shutdown.
- Added service discovery to identify healthy service instances.
- Implemented round-robin load distribution.
- Created a message producer and consumer using RabbitMQ concepts.
- Configured durable queues and persistent messages.
- Implemented idempotent event processing using event IDs.
- Created a serverless email notification function.
- Connected the message broker with the serverless function through an event bridge.
- Tested duplicate event handling to ensure that the same event was not processed multiple times.

**Concept