# infra/generate_presigned_put.py
import boto3
import sys
from urllib.parse import urlparse

def generate_presigned_put(bucket_name, key_name, expiration=3600):
    s3_client = boto3.client('s3', region_name='eu-central-1')
    
    signed_headers = {
        'x-amz-server-side-encryption': 'AES256'
    }

    url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket_name, 'Key': key_name, 'ServerSideEncryption': 'AES256'},
        ExpiresIn=expiration,
        HttpMethod='PUT'
    )
    return url

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_presigned_put.py <bucket> <key>")
        sys.exit(2)
    bucket = sys.argv[1]
    key = sys.argv[2]
    url = generate_presigned_put(bucket, key)
    print(url)