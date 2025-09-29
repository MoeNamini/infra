# tests/integration_test_lambda.py
import os
import time
import boto3
import pytest
from datetime import datetime

# Get AWS resources from environment or use defaults
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'lambdandynam-static-01-01123581321')
LAMBDA_NAME = os.environ.get('LAMBDA_NAME', 'lambda-static-01')
DYNAMO_TABLE = os.environ.get('DYNAMO_TABLE', 'dynamotable-static-01')
AWS_REGION = os.environ.get('AWS_REGION', 'eu-central-1')

@pytest.fixture
def aws_clients():
    """Create AWS service clients"""
    return {
        's3': boto3.client('s3', region_name=AWS_REGION),
        'lambda': boto3.client('lambda', region_name=AWS_REGION),
        'dynamodb': boto3.resource('dynamodb', region_name=AWS_REGION)
    }

def test_s3_upload_triggers_lambda_and_stores_in_dynamodb(aws_clients):
    """
    Integration test: Upload file to S3 -> Lambda processes -> DynamoDB stores metadata
    """
    s3 = aws_clients['s3']
    dynamodb = aws_clients['dynamodb']
    table = dynamodb.Table(DYNAMO_TABLE)
    
    # Arrange: Create a unique test file
    test_key = f"integration-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    test_content = b"Integration test content"
    
    # Clean up any existing item first
    try:
        table.delete_item(Key={'s3_key': test_key})
    except:
        pass
    
    try:
        # Act: Upload file to S3 (should trigger Lambda)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=test_key,
            Body=test_content
        )
        
        # Wait for Lambda to process (async trigger)
        time.sleep(5)
        
        # Assert: Check DynamoDB for the metadata
        response = table.get_item(Key={'s3_key': test_key})
        
        assert 'Item' in response, f"Item not found in DynamoDB for key: {test_key}"
        item = response['Item']
        
        # Verify the stored metadata
        assert item['s3_bucket'] == BUCKET_NAME
        assert item['s3_key'] == test_key
        assert 'processing_status' in item
        assert item['processing_status'] in ['RECEIVED', 'PROCESSED']
        assert 'timestamp' in item
        
        print(f"✅ Integration test passed! Item stored in DynamoDB: {item}")
        
    finally:
        # Cleanup: Delete test file from S3 and DynamoDB
        try:
            s3.delete_object(Bucket=BUCKET_NAME, Key=test_key)
            table.delete_item(Key={'s3_key': test_key})
        except Exception as e:
            print(f"Cleanup error: {e}")

def test_lambda_function_exists(aws_clients):
    """Verify Lambda function is deployed and accessible"""
    lambda_client = aws_clients['lambda']
    
    response = lambda_client.get_function(FunctionName=LAMBDA_NAME)
    
    assert response['Configuration']['FunctionName'] == LAMBDA_NAME
    assert response['Configuration']['Runtime'] == 'python3.10'
    assert response['Configuration']['State'] == 'Active'
    
    print(f"✅ Lambda function {LAMBDA_NAME} is active")

def test_dynamodb_table_exists(aws_clients):
    """Verify DynamoDB table exists and is accessible"""
    dynamodb = aws_clients['dynamodb']
    
    table = dynamodb.Table(DYNAMO_TABLE)
    table.load()
    
    assert table.table_status == 'ACTIVE'
    assert table.key_schema[0]['AttributeName'] == 's3_key'
    
    print(f"✅ DynamoDB table {DYNAMO_TABLE} is active")