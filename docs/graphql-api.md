# GraphQL API

The API uses a job-based asynchronous model.

## submitJob Mutation

Creates a new report job and returns immediately.

```graphql
mutation {
  submitJob(
    input: {
      reportType: "PAYROLL"
      clientId: "05184"
      startDate: "2026-01-01"
      endDate: "2026-12-31"
    }
  ) {
    id
    status
  }
}
```

## job Query

Retrieves job status and computed results.

```graphql
query {
  job(id: "JOB_ID") {
    status
    error
    result {
      resultCount
      reports {
        clientId
        planType
        coverageStartDate
        coverageEndDate
      }
    }
  }
}
```
