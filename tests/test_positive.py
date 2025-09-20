# infra/tests/test_s3_uploader.py
import boto3
from moto import mock_aws
from pathlib import Path

# This test confirms that a file can be successfully uploaded to a mock S3 bucket.
@mock_aws
def test_upload_file_successful():
    # 1. Setup a mock S3 environment
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-upload-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    # 2. Prepare a sample file to be uploaded
    file_content = b"This is some test content."
    file_path = Path("test.txt")
    file_path.write_bytes(file_content)

    # 3. Perform the upload action
    s3_client.put_object(Bucket=bucket_name, Key="test.txt", Body=file_content)

    # 4. Assert that the upload was successful and the content is correct
    # The 'get_object' call will fail if the file doesn't exist, serving as a positive assertion.
    retrieved_object = s3_client.get_object(Bucket=bucket_name, Key="test.txt")
    retrieved_content = retrieved_object["Body"].read()

    assert retrieved_content == file_content
    
    # Clean up the temporary file
    file_path.unlink()