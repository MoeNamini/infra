import os, json, boto3
from datetime import datetime
from botocore.exceptions import ClientError

# Use .get() with defaults for testing
REGION = os.environ.get('REGION', 'eu-central-1')
DDB_TABLE = os.environ.get('DDB_TABLE', 'processing-metadata')

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(DDB_TABLE)

def process_record(record_body):
    """Process a single message payload. Returns True on success."""
    body = json.loads(record_body)
    bucket = body.get('bucket')
    key = body.get('key')
    size = body.get('size')
    content_type = body.get('contentType')
    
    try:
        # conditional write helps idempotency
        table.put_item(
            Item={
                's3_key': key,
                'bucket': bucket,
                'file_size': size,
                'content_type': content_type,
                'processed_at': datetime.utcnow().isoformat()
            },
            ConditionExpression='attribute_not_exists(s3_key)'
        )
        return True
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            # Item already exists - idempotent, treat as success
            print(f"Item already exists (idempotent): {key}")
            return True
        else:
            print(f"ERROR processing record: {str(e)}")
            raise

def handler(event, context):
    processed = 0
    for record in event['Records']:
        processed += 1
        try:
            body = record['body']
            process_record(body)  # Use the extracted function
        except Exception as e:
            print("ERROR processing record:", str(e))
            raise
    return {"statusCode": 200, "body": json.dumps(f"Processed {processed} messages")}