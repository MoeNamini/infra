# scripts/lambda_handler.py
import json
import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DDB_TABLE = os.environ.get("DDB_TABLE", "processing-metadata")
REGION = os.environ.get("AWS_REGION", "eu-central-1")

s3 = boto3.client("s3", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)

def handler(event, context):
    """
    Lambda handler triggered by S3 ObjectCreated event.
    It writes metadata to DynamoDB:
      - bucket, key, size, content_type, processing_status
    """
    records = event.get("Records", [])
    results = []
    table = dynamodb.Table(DDB_TABLE)
    for r in records:
        try:
            bucket = r["s3"]["bucket"]["name"]
            key = r["s3"]["object"]["key"]
            # get object head
            head = s3.head_object(Bucket=bucket, Key=key)
            size = head.get("ContentLength")
            ctype = head.get("ContentType")
            # Optionally read small file (caution: don't read large files)
            # obj = s3.get_object(Bucket=bucket, Key=key)
            # content_snippet = obj['Body'].read(1024).decode('utf-8', errors='ignore')
            item = {
                "s3_bucket": bucket,
                "s3_key": key,
                "size": size,
                "content_type": ctype,
                "processing_status": "RECEIVED"
            }
            # put into DynamoDB
            table.put_item(Item=item)
            logger.info("Wrote metadata to DynamoDB for %s/%s", bucket, key)
            results.append({"key": key, "status": "ok"})
        except ClientError as e:
            logger.exception("S3/Dynamo operation failed for record: %s", e)
            results.append({"key": key if 'key' in locals() else None, "status": "error", "error": str(e)})
    return {"results": results}