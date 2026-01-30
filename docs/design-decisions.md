# Design Decisions

## Why asynchronous jobs?

Report generation can be long-running and expensive. Async jobs:

- avoid API timeouts
- enable background processing
- support fire-and-forget workflows
- allow result caching for later retrieval

## Why SQS?

SQS provides:

- decoupling between API and processing
- automatic retries
- DLQ routing for poison messages
- the ability to smooth traffic spikes

## Why DynamoDB?

DynamoDB is a strong fit for job state:

- fast key-based lookups by `jobId`
- flexible schema for evolving results
- TTL support for cleanup
- minimal operational overhead

## Why polling instead of subscriptions?

Polling:

- keeps the client simple
- avoids websocket/subscription complexity
- matches common enterprise reporting workflows

## Why mock data?

This project focuses on architecture and reliability patterns. Mock data enables:

- deterministic outputs
- reproducible tests
- zero external dependencies
