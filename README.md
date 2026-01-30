# Async Report Generator (AWS Serverless + GraphQL)

A serverless asynchronous report generation service built with **AWS AppSync, Lambda, SQS, DynamoDB, and CloudWatch**.  
Designed to demonstrate production-grade patterns for long-running jobs, background processing, and reliable result retrieval.

---

## Overview

This project implements an **asynchronous reporting pipeline** commonly used in enterprise HR, payroll, and finance systems.

Instead of blocking API requests while generating complex reports, the system uses a **job-based model**:

1. Client submits a report request
2. Job is created and queued
3. Background worker generates the report
4. Client polls for status and results

This pattern ensures scalability, fault tolerance, and clean separation between API and processing layers.

---

## Key Concepts Demonstrated

- Async job orchestration
- GraphQL + background processing
- Queue-based retry handling
- Dead-letter queues (DLQ)
- DynamoDB job state modeling
- Deterministic report generation
- Polling-based API design
- Production-grade failure handling

---

## Architecture
<pre>
Client
  │
  ▼
  AWS AppSync (GraphQL)
    │
    ▼
    submitJob Lambda
      │
      ├─ Write job record (QUEUED) → DynamoDB (jobs table)
      └─ Send message → SQS Queue (+ DLQ)
        │
        ▼
        job_worker Lambda
          │
          ├─ Update job → RUNNING
          ├─ Generate report (filter + aggregate)
          ├─ Persist result
          └─ Update job → SUCCEEDED / FAILED
</pre>
---

## Job Lifecycle

Each report follows a strict lifecycle:

| Status | Description |
|------|-------------|
| QUEUED | Job created and awaiting processing |
| RUNNING | Worker actively generating report |
| SUCCEEDED | Report generated successfully |
| FAILED | Processing failed (error captured) |

Failures are retried automatically by SQS. After max retries, messages are moved to the **Dead Letter Queue (DLQ)**.

---

## Data Model

### DynamoDB – jobs Table

Each job record includes:

- `jobId` (partition key)
- `status`
- `input` (original request)
- `result` (generated report)
- `error` (if failed)
- `attemptCount`
- `lastErrorAt`
- `createdAt`
- `updatedAt`
- `expiresAt` (TTL cleanup)

Old jobs automatically expire using DynamoDB TTL.

---

## Report Generation

Reports are generated using **deterministic mock datasets** to simulate real payroll and benefits data.

Supported filters:
- `clientId` (optional)
- `planType` (optional)
- coverage date range (required)

Filtering logic is applied **only when fields are provided**, mirroring real-world GraphQL input behavior.

### Example report result structure

```json
{
  "resultCount": 1,
  "filtersApplied": {
    "clientId": "05184",
    "planType": null,
    "startDate": "2025-01-01",
    "endDate": "2025-06-01"
  },
  "reports": [
    {
      "clientId": "05184",
      "planType": "FSA",
      "coverageStartDate": "2025-01-01",
      "coverageEndDate": "2025-06-01",
      "summary": {
        "totalEmployees": 1320,
        "totalDeductions": 113245.90
      }
    }
  ]
}
