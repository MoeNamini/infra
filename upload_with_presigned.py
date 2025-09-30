# infra/upload_with_presigned.py
import sys
import requests

def upload_file_with_presigned(url, local_path):
    # Add the encryption header to the upload request
    headers = {
        'x-amz-server-side-encryption': 'AES256'
    }

    with open(local_path, 'rb') as f:
        resp = requests.put(url, data=f, headers=headers)
    print("Status code:", resp.status_code)
    if not resp.ok:
        print("Response headers:", resp.headers)
        print("Response text:", resp.text)
    return resp.ok

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python upload_with_presigned.py <presigned_url> <local_file>")
        sys.exit(2)
    url = sys.argv[1]
    path = sys.argv[2]
    ok = upload_file_with_presigned(url, path)
    sys.exit(0 if ok else 1)