# Evidence Summary — Day 5 (S3 → SQS → Lambda → DynamoDB Integration)

## Overview
This document maps each collected artifact to its purpose and acceptance criteria (AC).

---

### 📦 Provisioning Evidence
| Artifact | What It Proves | Acceptance Criteria |
|-----------|----------------|--------------------|
| `artifacts/CF-outputs.json` | Contains CloudFormation stack outputs such as `ProcessingQueueUrl`, `DLQUrl`, `LambdaArn`, `TableName`, confirming all required resources were created. | AC-1: CloudFormation stack successfully deployed and outputs captured. |
| `artifacts/stack-events.json` | Shows the chronological deployment process of each resource; verifies no CREATE_FAILED events. | AC-1 |

---

### 🔄 Integration Flow Evidence
| Artifact | What It Proves | Acceptance Criteria |
|-----------|----------------|--------------------|
| `artifacts/integration-test-output.txt` | Console output of full test run: S3 upload → SQS trigger → Lambda processing → DynamoDB write. | AC-2: Integration pipeline functions end-to-end. |
| `artifacts/integration-junit.xml` | XML version of the same test, machine-readable for CI dashboards. | AC-3: Tests pass in automated environment. |
| `artifacts/dynamodb_item_testfile.json` | The processed item retrieved from DynamoDB with `processing_status=done` and correct attributes. | AC-4: Lambda successfully wrote data to DynamoDB. |
| `artifacts/lambda_logs_window.json` | CloudWatch logs confirming Lambda invocation, successful processing, and duration. | AC-4 |
| `artifacts/queue_attributes.json` | Output of `aws sqs get-queue-attributes`, showing both main queue and DLQ are empty. | AC-5: No messages stuck in main or DLQ after run. |
| `artifacts/dlq_msg.json` | (Optional) Used if test failed. Shows message body and failure reason for debugging. | AC-5 (Negative Scenario). |

---

### 🧰 Supporting Artifacts
| Artifact | What It Proves | Acceptance Criteria |
|-----------|----------------|--------------------|
| `artifacts/policy-least-privilege.json` | IAM policy allowing only required actions (`s3:PutObject`, `sqs:SendMessage`, `dynamodb:PutItem`). | AC-6: Least privilege enforced. |
| `artifacts/event-source-mapping.json` | Output of `aws lambda list-event-source-mappings`. Confirms SQS → Lambda binding active. | AC-7: Correct event source mapping configured. |
| `artifacts/queue_arns.json` | Proof of SQS and DLQ ARNs for IAM references. | AC-8: Resource ARNs captured for audit. |

---

### 🧩 Design Rationale (Narrative Evidence)
| Document | What It Explains | Why It Matters |
|-----------|------------------|----------------|
| `docs/day5-infra.md` | Architecture overview and design reasoning (why SQS, DLQ, conditional writes). | Shows system-level understanding. |
| `docs/30min-audit.md` | Step-by-step reproduction guide for reviewers. | Demonstrates reproducibility and PM-level documentation. |

---

**Total artifacts collected:** 12  
**Validation date:** 2025-10-08  
**Test region:** `eu-central-1`  
**AWS account:** `<ACCOUNT_ID>`
