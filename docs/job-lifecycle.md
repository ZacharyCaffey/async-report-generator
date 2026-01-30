# Job Lifecycle

Each report request follows a strict lifecycle and is persisted in DynamoDB for client polling.

## States

| Status | Description |
|------|-------------|
| QUEUED | Job created and awaiting processing |
| RUNNING | Worker actively generating report |
| SUCCEEDED | Report completed successfully |
| FAILED | Processing failed (error captured) |

## Lifecycle Flow

1. Client calls `submitJob`
2. `submit_job` creates job record with status `QUEUED`
3. `submit_job` enqueues `{ jobId, input }` to SQS
4. `job_worker` consumes message and sets job to `RUNNING`
5. `job_worker` generates the report
6. `job_worker` writes result and sets status to `SUCCEEDED` (or `FAILED` on error)

## Retry Behavior

- SQS automatically retries failed messages
- Each worker attempt increments `attemptCount`
- After max receives, message moves to the DLQ

## Failure Handling

When a job fails:
- `status = FAILED`
- `error` contains a readable message
- `lastErrorAt` records the last failure timestamp
