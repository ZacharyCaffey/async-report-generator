import json, os, uuid
from datetime import datetime, timezone
import boto3
import time

table = boto3.resource("dynamodb").Table(os.environ["JOBS_TABLE"])
sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]

def now():
  return datetime.now(timezone.utc).isoformat()

def lambda_handler(event, context):
  job_input = (event.get("arguments") or {}).get("input") or {}
  job_id = str(uuid.uuid4())
  ts = now()
  TTL_DAYS = 7
  expires_at = int(time.time()) + (TTL_DAYS * 24 * 60 * 60)

  for k in ["reportType", "clientId", "startDate", "endDate"]:
    if not job_input.get(k):
      raise ValueError(f"Missing required field: {k}")

  item = {
    "jobId": job_id,
    "id": job_id,
    "type": job_input["reportType"],
    "status": "QUEUED",
    "input": job_input,
    "result": None,
    "error": None,
    "createdAt": ts,
    "updatedAt": ts,
    "attemptCount": 0,
    "lastErrorAt": None,
    "expiresAt": expires_at,
  }
  table.put_item(Item=item)

  sqs.send_message(
    QueueUrl=QUEUE_URL,
    MessageBody=json.dumps({"jobId": job_id, "input": job_input})
  )

  return {
    "id": job_id,
    "type": job_input["reportType"],
    "status": "QUEUED",
    "result": None,
    "error": None,
    "createdAt": ts,
    "updatedAt": ts,
    "attemptCount": 0,
    "lastErrorAt": None,
  }
