# Report Generation

Reports are generated from deterministic mock datasets to simulate payroll/benefits reporting.

## Supported Filters

Filters are applied conditionally based on GraphQL input:
- `clientId` (optional)
- `planType` (optional)
- requested date range (required)

Only provided filters are applied.

## Date Range Matching

A report is included when its coverage period overlaps the requested window:
- overlap = `requestedStart <= reportEnd AND requestedEnd >= reportStart`

## Deterministic Output

Given the same inputs, results remain consistent. This improves:
- repeatable testing
- predictable demos
- easier debugging

## Summary Metrics

Each report includes summary-level metrics such as:
- `totalEmployees` or `totalEnrollments`
- `totalDeductions`

Numeric values are stored using `Decimal` to align with DynamoDB constraints.
