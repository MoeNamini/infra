#!/usr/bin/env bash
set -e

# Use provided arguments or default values
POLICY_NAME=${1:-HybridS3UploaderPolicy}
POLICY_FILE=${2:-infra/new-policy.json}

# Create the policy and capture the ARN into a script variable
POLICY_ARN=$(aws iam create-policy --policy-name "$POLICY_NAME" --policy-document file://"$POLICY_FILE" \
  | jq -r '.Policy.Arn')

# Check if the ARN was captured successfully
if [[ -z "$POLICY_ARN" ]]; then
    echo "Error: Could not capture Policy ARN. Check previous command output." >&2
    exit 1
fi

# Print the result to the screen for confirmation
echo "✅ Policy ARN created: $POLICY_ARN"

# Append the ARN to the markdown file
echo "Policy ARN: $POLICY_ARN" >> iam-setup-template.md