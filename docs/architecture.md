# Architecture

This service implements an asynchronous report generation pipeline using AWS serverless components.

The architecture separates request handling from long-running computation to ensure scalability and reliability.

## High-Level Flow

Client → AppSync → Lambda → SQS → Lambda → DynamoDB

Client
│
▼
AWS AppSync (GraphQL)
│
▼
submitJob Lambda
│
├─ Write job record (QUEUED)
└─ Enqueue message to SQS
│
▼
SQS Queue (+ DLQ)
│
▼
job_worker Lambda
│
├─ Update job → RUNNING
├─ Generate report
├─ Persist result
└─ Update job → SUCCEEDED / FAILED


## Components

### AWS AppSync
Provides the GraphQL API layer used to submit jobs and query job status/results.

### submit_job Lambda
- Validates GraphQL input
- Generates a `jobId`
- Writes job metadata to DynamoDB
- Sends a message to SQS for background processing

### SQS Queue
- Buffers report jobs
- Enables retries
- Decouples API from computation

### Dead Letter Queue (DLQ)
- Captures messages that fail after max retry attempts
- Prevents poison messages from blocking processing
- Enables inspection and replay of failed messages

### job_worker Lambda
- Triggered automatically by SQS
- Performs report generation
- Updates job lifecycle state
- Persists results or errors to DynamoDB

### DynamoDB
- Stores job state and results for polling
- Enables fast key-based lookups by `jobId`
- Uses TTL (`expiresAt`) for automatic cleanup

### CloudWatch
- Centralized logging for `submit_job` and `job_worker`
- Metrics and alarms for Lambda errors, queue depth, and DLQ activity
- Primary place to debug failed jobs (stack traces + request context)
