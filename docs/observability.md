# Observability & Reliability

This service is designed to be debuggable and resilient under failure conditions.

## Logging

- Both Lambdas emit logs to CloudWatch
- Logs include `jobId` for traceability
- Worker logs include lifecycle transitions and errors

## Metrics

Key metrics to monitor:
- Lambda invocations and error rate
- SQS queue depth (available + in-flight)
- DLQ message count

## Retries

- Failures trigger automatic retries via SQS
- Retry attempts are visible via `attemptCount` in DynamoDB
- Persistent failures route to the DLQ for inspection

## Dead Letter Queue (DLQ)

Messages land in the DLQ when max retries are exceeded. This enables:
- isolating poison messages
- debugging failures without blocking processing
- optional replay after fixes

## Client Visibility

Job status, errors, and results are persisted to DynamoDB so clients can observe:
- `status`
- `error`
- `attemptCount`
- `lastErrorAt`
without needing direct CloudWatch access.
