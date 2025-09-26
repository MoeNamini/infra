# Presign Workflow Template (copy & reuse)

> Copy this file at the start of any new presign/S3 workflow and replace the placeholders.

## Basic info
- Project: Presign workflow 
- Author: MoeNamini 
- Date: Sep 2025 

## Purpose
Generate pre-signed S3 PUT URLs for clients, require server-side encryption (SSE), validate via unit & integration tests, and publish CI artifacts.

## Replaceable placeholders
- `<BUCKET>` — S3 bucket name you will use (for integration or verification)
- `<PROFILE>` — AWS CLI profile (for verification steps only)
- `<REGION>` — AWS region (e.g., eu-central-1)
- `<POLICY_ARN>` — managed policy ARN (paste after create)
- `<ROLE_ARN>` — role ARN (if applicable)
- `<TEST_ACCOUNT_ID>` — account id used for integration tests (if you restrict policy)

## Pre-reqs
- AWS CLI v2 installed and configured locally
- `python3`, `pip`, `virtualenv` / venv available
- `requests`, `boto3`, `pytest` in `requirements.txt`

## Server-side script (generator)
File: `scripts/generate_presigned_put.py`
- Usage: `python scripts/generate_presigned_put.py <BUCKET> <KEY> [--expires 3600] [--sse AES256 | aws:kms]`
- Output: prints presigned URL to stdout

## Client-side upload
File: `scripts/upload_with_presigned.py`
- Usage: `python scripts/upload_with_presigned.py "<PRESIGNED_URL>" <LOCAL_FILE> [SSE_HEADER]`
- Example: `python scripts/upload_with_presigned.py "$(cat presigned_url.txt)" test.txt AES256`

## Unit tests (fast)
File: `tests/test_presign_unit.py`
- Command: `pytest tests/test_presign_unit.py -q`
- Purpose: mock boto3, assert `generate_presigned_url` called with `ServerSideEncryption` when requested.

## Integration tests (gated)
File: `tests/integration_test_presign.py`
- Command (manual): 
  ```bash
  export AWS_PROFILE=<PROFILE>
  export AWS_REGION=<REGION>
  pytest tests/integration_test_presign.py -q
  ```
- Purpose: create temp bucket, generate presign, upload file via HTTP PUT, verify object, cleanup.

## CI (recommended)
- Workflow: `.github/workflows/ci-presign-test.yml`  
  - Run unit tests on push/PR.
  - Upload `test-results.txt` and `artifacts/junit.xml` as artifacts.
  - Integration tests run manually or when `RUN_INTEGRATION=true` (gated).

## Acceptance criteria (copy into issue/PR)
- AC1: Unit tests pass in CI (mocked boto3).
- AC2: Presigned generator supports SSE when `--sse` passed.
- AC3: Client upload works with SSE header; integration test (manual) completes end-to-end.
- AC4: CI artifacts uploaded and linked in PR.
- AC5: `iam-setup-template.md` updated with `Policy.Arn`, `Role.Arn`, and steps to reproduce tests.

## Example "proof" snippets to paste into PR or evidence report
- `Policy.Arn: <POLICY_ARN>`
- `pytest` 1-line snippet:
  ```
  $ pytest tests/test_presign_unit.py -q | head -n 2
  ============================= test session starts ==============================
  1 passed in 0.12s
  ```
- `aws s3api get-bucket-encryption` example to paste:
  ```json
  {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }
  ```

## Troubleshooting quick commands
- Validate JSON: `jq . tests/bucket-policy.json`
- Simulate policy: `aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::<ID>:user/<USER> --action-names s3:PutObject --resource-arns arn:aws:s3:::<BUCKET>/*`
- Show requester identity: `aws sts get-caller-identity --profile <PROFILE>`

## Cleanup after integration run
1. Delete objects: `aws s3 rm s3://<TEMP_BUCKET> --recursive --profile <PROFILE>`
2. Delete bucket: `aws s3api delete-bucket --bucket <TEMP_BUCKET> --profile <PROFILE>`

---

## Notes
- Keep integration runs to dedicated test accounts to avoid accidental production changes or costs.
- Do not commit secrets. Use GitHub Secrets for CI credentials.
