# tests/integration_test_sqs.py
import os
import time
import uuid
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# Configuration via environment variables (set these before running)
REGION = os.environ.get("AWS_REGION", "eu-central-1")
PROFILE = os.environ.get("AWS_PROFILE")   # optional
BUCKET = os.environ.get("INTEGRATION_BUCKET")  # required
TABLE = os.environ.get("INTEGRATION_TABLE")    # required (DynamoDB)
LAMBDA_NAME = os.environ.get("LAMBDA_NAME")    # required (processor lambda)
QUEUE_URL = os.environ.get("QUEUE_URL")        # required (SQS queue url)
DLQ_URL = os.environ.get("DLQ_URL")            # required (DLQ queue url)
POLL_TIMEOUT = int(os.environ.get("POLL_TIMEOUT", "120"))  # seconds
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "3"))

if not (BUCKET and TABLE and LAMBDA_NAME and QUEUE_URL and DLQ_URL):
    raise SystemExit("Please set INTEGRATION_BUCKET, INTEGRATION_TABLE, LAMBDA_NAME, QUEUE_URL and DLQ_URL env vars")

# Create a boto3 session (respects AWS_PROFILE if set in env)
session = boto3.Session(region_name=REGION)
s3 = session.client("s3")
ddb = session.client("dynamodb")
logs = session.client("logs")
sqs = session.client("sqs")

def mk_key():
    return f"integration/{int(time.time())}-{uuid.uuid4().hex[:8]}.txt"

def upload_file_to_s3(local_path, bucket, key):
    print(f"[upload] {local_path} -> s3://{bucket}/{key}")
    s3.upload_file(Filename=local_path, Bucket=bucket, Key=key)

def poll_dynamodb_for_key(table, key, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
    deadline = time.time() + timeout
    print(f"[poll] waiting up to {timeout}s for key {key} in table {table}")
    while time.time() < deadline:
        try:
            resp = ddb.get_item(TableName=table, Key={"s3_key": {"S": key}})
        except ClientError as e:
            print("[ddb] get_item error:", e)
            time.sleep(interval)
            continue
        if "Item" in resp:
            return resp["Item"]
        time.sleep(interval)
    return None

def get_queue_count(queue_url):
    attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages","ApproximateNumberOfMessagesNotVisible"])
    return {k: int(attrs["Attributes"].get(k, "0")) for k in ("ApproximateNumberOfMessages","ApproximateNumberOfMessagesNotVisible")}

def fetch_lambda_logs(function_name, start_ms, end_ms, max_events=200):
    log_group = f"/aws/lambda/{function_name}"
    try:
        resp = logs.filter_log_events(logGroupName=log_group, startTime=start_ms, endTime=end_ms, interleaved=True, limit=max_events)
        return resp.get("events", [])
    except Exception as e:
        print("[logs] error:", e)
        return []

def save_artifact(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, default=str, indent=2)
    print("[artifact] wrote", str(path))

def cleanup_s3_ddb(bucket, key, table):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print("[cleanup] s3 delete warning:", e)
    try:
        ddb.delete_item(TableName=table, Key={"s3_key": {"S": key}})
    except Exception as e:
        print("[cleanup] ddb delete warning:", e)

def main():
    # prepare local sample file
    p = Path("test.txt")
    if not p.exists():
        p.write_text("integration test body\n")

    key = mk_key()
    print("[test] use key:", key)

    start_ms = int(time.time() * 1000) - 5000
    upload_file_to_s3(str(p), BUCKET, key)

    # poll for ddb item
    item = poll_dynamodb_for_key(TABLE, key)
    end_ms = int(time.time() * 1000) + 5000

    # fetch lambda logs
    events = fetch_lambda_logs(LAMBDA_NAME, start_ms, end_ms)

    # queue attributes
    queue_attrs = get_queue_count(QUEUE_URL)
    dlq_attrs = get_queue_count(DLQ_URL)

    # artifacts folder
    artifacts = Path("artifacts")
    artifacts.mkdir(exist_ok=True)

    save_artifact(artifacts / f"dynamodb_item_{key.replace('/', '_')}.json", item if item else {"found": False})
    save_artifact(artifacts / f"lambda_logs_{key.replace('/', '_')}.json", events)
    save_artifact(artifacts / "queue_attributes.json", {"queue": queue_attrs, "dlq": dlq_attrs})

    # print verification summary
    found = bool(item)
    print("[summary] dynamodb item found:", found)
    if found:
        # check processing_status if present
        status = item.get("processing_status", {}).get("S") if isinstance(item, dict) else None
        print("[summary] processing_status (raw):", status)
    print("[summary] queue attrs:", queue_attrs)
    print("[summary] dlq attrs:", dlq_attrs)

    # cleanup resources (S3 object and ddb item)
    cleanup_s3_ddb(BUCKET, key, TABLE)

    # determine success conditions to return code for pytest (non-zero -> fail)
    ok = found and (int(queue_attrs.get("ApproximateNumberOfMessages",0)) == 0) and (int(dlq_attrs.get("ApproximateNumberOfMessages",0)) == 0)
    if not ok:
        print("[result] Integration test FAILED")
        raise SystemExit(2)
    print("[result] Integration test PASSED")
    return 0

if __name__ == "__main__":
    main()
