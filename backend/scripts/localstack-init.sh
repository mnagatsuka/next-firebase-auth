#!/usr/bin/env bash
set -euo pipefail

echo "[localstack-init] Initializing DynamoDB tables..."

# Helper to create a table if it does not exist
create_table_if_missing() {
  local TABLE_NAME="$1"
  local KEY_NAME="$2"

  if awslocal dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
    echo "[localstack-init] Table '$TABLE_NAME' already exists. Skipping."
    return 0
  fi

  echo "[localstack-init] Creating table '$TABLE_NAME'..."
  awslocal dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName="$KEY_NAME",AttributeType=S \
    --key-schema AttributeName="$KEY_NAME",KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
}

# Default names match docker-compose env; LocalStack sees env from service not needed here
POSTS_TABLE=${APP_DYNAMODB_TABLE_POSTS:-posts}
COMMENTS_TABLE=${APP_DYNAMODB_TABLE_COMMENTS:-comments}

create_table_if_missing "$POSTS_TABLE" id
create_table_if_missing "$COMMENTS_TABLE" id

echo "[localstack-init] DynamoDB initialization complete."

