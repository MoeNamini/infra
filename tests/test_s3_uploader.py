# infra/tests/test_s3_upload.py
import boto3
from moto import mock_aws
from pathlib import Path
import pytest

# import the function from your script (script.py must be at repo root)
from script import upload_file


@mock_aws
def test_upload_file(tmp_path):
    # choose region for client
    region = "eu-central-1"
    s3 = boto3.client("s3", region_name=region)

    bucket = "test-bucket"

    # create bucket; for non-us-east-1, include LocationConstraint
    if region == "us-east-1":
        s3.create_bucket(Bucket=bucket)
    else:
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region})

    # prepare a sample file in a temporary directory (pytest tmp_path fixture)
    p = tmp_path / "test.txt"
    p.write_text("hello")

    # call the uploader function directly (in-process so moto intercepts boto3)
    assert upload_file(str(p), bucket=bucket, key="test.txt", region=region) is True

    # validate object exists and content matches
    obj = s3.get_object(Bucket=bucket, Key="test.txt")
    content = obj["Body"].read().decode("utf-8")
    assert content == "hello"
