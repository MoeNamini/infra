# script.py
import argparse
from pathlib import Path
import boto3
from typing import Optional, Union


def s3_client(region_name: Optional[str] = None, endpoint_url: Optional[str] = None):
    kwargs = {}
    if region_name:
        kwargs["region_name"] = region_name
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.client("s3", **kwargs)


def upload_file(path: Union[str, Path], bucket: str, key: str,
                region: Optional[str] = None, endpoint_url: Optional[str] = None) -> bool:
    """
    Uploads a local file to S3 using boto3 client.
    Returns True on success, raises exception on failure.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    client = s3_client(region_name=region, endpoint_url=endpoint_url)

    # Read bytes and put object (works for tests with moto)
    with path.open("rb") as f:
        client.put_object(Bucket=bucket, Key=key, Body=f.read())

    return True


def main():
    parser = argparse.ArgumentParser(description="Upload a file to S3")
    parser.add_argument("--file", required=True, help="Local path to file")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--key", required=True, help="S3 object key")
    parser.add_argument("--region", default=None, help="AWS region (optional)")
    parser.add_argument("--endpoint-url", default=None, help="S3 endpoint (for testing)")

    args = parser.parse_args()
    upload_file(args.file, args.bucket, args.key, region=args.region, endpoint_url=args.endpoint_url)


if __name__ == "__main__":
    main()
