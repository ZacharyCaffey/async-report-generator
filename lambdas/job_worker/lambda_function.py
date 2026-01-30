import json, os
from datetime import datetime, timezone
import boto3
from decimal import Decimal

table = boto3.resource("dynamodb").Table(os.environ["JOBS_TABLE"])

def now():
  return datetime.now(timezone.utc).isoformat()

def mark_running_and_increment(job_id: str):
  table.update_item(
    Key={"jobId": job_id},
    UpdateExpression="SET #s = :running, updatedAt = :u ADD attemptCount :inc",
    ExpressionAttributeNames={"#s": "status"},
    ExpressionAttributeValues={
      ":running": "RUNNING",
      ":u": now(),
      ":inc": Decimal(1),
    },
)

def parse_date(s: str) -> datetime:
  return datetime.strptime(s, "%Y-%m-%d")

def overlaps(a_start, a_end, b_start, b_end) -> bool:
  return a_start <= b_end and a_end >= b_start

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

def update_job(job_id, status, result=None, error=None):
  expr = "SET #s = :s, #u = :u"
  names = {"#s": "status", "#u": "updatedAt"}
  values = {":s": status, ":u": now()}

  if result is not None:
    expr += ", #r = :r"
    names["#r"] = "result"
    values[":r"] = result

  if error is not None:
    expr += ", #e = :e"
    names["#e"] = "error"
    values[":e"] = error

  table.update_item(
    Key={"jobId": job_id},
    UpdateExpression=expr,
    ExpressionAttributeNames=names,
    ExpressionAttributeValues=values,
  )

def mark_failed(job_id: str, err: str):
  table.update_item(
    Key={"jobId": job_id},
    UpdateExpression="SET #s = :failed, updatedAt = :u, #e = :e, lastErrorAt = :t",
    ExpressionAttributeNames={"#s": "status", "#e": "error"},
    ExpressionAttributeValues={
      ":failed": "FAILED",
      ":u": now(),
      ":e": err,
      ":t": now(),
    },
  )

def lambda_handler(event, context):
  for record in event.get("Records", []):
    body = json.loads(record["body"])
    job_id = body["jobId"]
    job_input = body["input"]

    try:
      mark_running_and_increment(job_id)
      report = generate_report(job_input)
      update_job(job_id, "SUCCEEDED", result=report)
    except Exception as e:
      mark_failed(job_id, str(e))
      update_job(job_id, "FAILED", error=str(e))
      raise  # important: lets SQS retry, then DLQ if it keeps failing
