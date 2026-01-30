from datetime import datetime, timezone
from decimal import Decimal

def now():
  return datetime.now(timezone.utc).isoformat()

def parse_date(s: str) -> datetime:
  return datetime.strptime(s, "%Y-%m-%d")

def overlaps(a_start, a_end, b_start, b_end) -> bool:
  return a_start <= b_end and a_end >= b_start

# ---- mock dataset ----
REPORTS = [
  {
    "clientId": "05389",
    "planType": "HSA",
    "coverageStartDate": "2025-01-01",
    "coverageEndDate": "2025-06-01",
    "summary": {
        "totalEmployees": 123,
        "totalDeductions": Decimal("45678.90"),
    },
  },
  {
    "clientId": "05184",
    "planType": "FSA",
    "coverageStartDate": "2025-01-01",
    "coverageEndDate": "2025-06-01",
    "summary": {
        "totalEmployees": 1320,
        "totalDeductions": Decimal("113245.90"),
    },
  },
  {
    "clientId": "05667",
    "planType": "HDV",
    "coverageStartDate": "2025-06-01",
    "coverageEndDate": "2025-12-31",
    "summary": {
        "totalEmployees": 14,
        "totalDeductions": Decimal("23693.90"),
    },
  },
  {
    "clientId": "05384",
    "planType": "HRA",
    "coverageStartDate": "2025-06-01",
    "coverageEndDate": "2025-12-31",
    "summary": {
        "totalEmployees": 3041,
        "totalDeductions": Decimal("1432874.90"),
    },
  },
]

def generate_report(job_input):
  reports = [
    {"clientId":"05389","planType":"HSA","coverageStartDate":"2025-01-01","coverageEndDate":"2025-06-01",
      "summary":{"totalEnrollments":123,"totalDeductions":Decimal("45678.90")}},
    {"clientId":"05184","planType":"FSA","coverageStartDate":"2025-01-01","coverageEndDate":"2025-06-01",
      "summary":{"totalEnrollments":1320,"totalDeductions":Decimal("113245.90")}},
    {"clientId":"05667","planType":"HDV","coverageStartDate":"2025-06-01","coverageEndDate":"2025-12-31",
      "summary":{"totalEnrollments":14,"totalDeductions":Decimal("23693.90")}},
    {"clientId":"05384","planType":"HRA","coverageStartDate":"2025-06-01","coverageEndDate":"2025-12-31",
      "summary":{"totalEnrollments":3041,"totalDeductions":Decimal("1432874.90")}},
  ]

  req_start = parse_date(job_input["startDate"])
  req_end = parse_date(job_input["endDate"])

  # optional filters from GraphQL input
  client_filter = job_input.get("clientId")
  plan_filter = job_input.get("planType")

  matched = []
  for r in reports:
    # apply only if clientId provided
    if client_filter and r["clientId"] != client_filter:
      continue

    # apply only if planType provided
    if plan_filter and r["planType"] != plan_filter:
      continue

    # always apply date range overlap
    r_start = parse_date(r["coverageStartDate"])
    r_end = parse_date(r["coverageEndDate"])
    if not overlaps(req_start, req_end, r_start, r_end):
      continue

    matched.append({
      **r,
      "reportType": job_input["reportType"],
      "generatedAt": now(),
    })

  return {
    "filtersApplied": {
      "clientId": client_filter,
      "planType": plan_filter,
      "startDate": job_input["startDate"],
      "endDate": job_input["endDate"],
    },
    "resultCount": len(matched),
    "reports": matched,
    "generatedAt": now(),
  }

# ---- test runner ----
def print_case(name: str, job_input: dict) -> None:
  out = generate_report(job_input)
  print(f"\n=== {name} ===")
  print("filtersApplied:", out["filtersApplied"])
  print("resultCount:", out["resultCount"])
  print("matched:", [(r["clientId"], r["planType"], r["coverageStartDate"], r["coverageEndDate"]) for r in out["reports"]])

def main():
  cases = [
    (
      "clientId only",
      {"reportType": "PAYROLL", "clientId": "05184", "startDate": "2025-01-01", "endDate": "2025-06-01"},
    ),
    (
      "planType only",
      {"reportType": "PAYROLL", "planType": "HSA", "startDate": "2025-01-01", "endDate": "2025-06-01"},
    ),
    (
      "clientId + planType",
      {"reportType": "PAYROLL", "clientId": "05389", "planType": "HSA", "startDate": "2025-01-01", "endDate": "2025-06-01"},
    ),
    (
      "date range overlap",
      {"reportType": "PAYROLL", "startDate": "2025-05-15", "endDate": "2025-06-15"},
    ),
    (
      "no matches",
      {"reportType": "PAYROLL", "clientId": "00000", "startDate": "2025-01-01", "endDate": "2025-12-31"},
    ),
  ]

  for name, job_input in cases:
    print_case(name, job_input)

if __name__ == "__main__":
  main()
