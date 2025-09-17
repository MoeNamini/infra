# infra/tests/test_s3_upload.py
import boto3
from moto import mock_aws
import os
import pytest
from botocore.exceptions import ClientError
from pathlib import Path
import subprocess

@mock_aws
def test_upload_file():
    # create mock bucket
    region = "eu-central-1"
    s3 = boto3.client("s3", region_name=region)

    bucket = "test-bucket"
    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={"LocationConstraint": region}
    )

    # prepare a sample file
    p = Path("infra/test.txt")
    p.write_text("hello")

    # call the script (ensure it uses default credentials in moto environment)
    res = subprocess.run(["python3", "script.py", "--file", str(p), "--bucket", bucket, "--key", "test.txt"], capture_output=True, text=True)
    assert res.returncode == 0

    # validate object exists
    content = s3.get_object(Bucket=bucket, Key="test.txt")["Body"].read().decode("utf-8")
    assert content == "hello"