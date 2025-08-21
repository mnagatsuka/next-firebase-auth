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

# Helper to create a table with composite key if it does not exist
create_table_composite_if_missing() {
  local TABLE_NAME="$1"
  local HASH_KEY_NAME="$2"
  local RANGE_KEY_NAME="$3"

  if awslocal dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
    echo "[localstack-init] Table '$TABLE_NAME' already exists. Skipping."
    return 0
  fi

  echo "[localstack-init] Creating composite-key table '$TABLE_NAME'..."
  awslocal dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName="$HASH_KEY_NAME",AttributeType=S AttributeName="$RANGE_KEY_NAME",AttributeType=S \
    --key-schema AttributeName="$HASH_KEY_NAME",KeyType=HASH AttributeName="$RANGE_KEY_NAME",KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
}

# Default names match docker-compose env; LocalStack sees env from service not needed here
POSTS_TABLE=${APP_DYNAMODB_TABLE_POSTS:-posts}
COMMENTS_TABLE=${APP_DYNAMODB_TABLE_COMMENTS:-comments}
FAVORITES_TABLE=${APP_DYNAMODB_TABLE_FAVORITES:-favorites}

create_table_if_missing "$POSTS_TABLE" id
create_table_if_missing "$COMMENTS_TABLE" id
create_table_composite_if_missing "$FAVORITES_TABLE" user_id post_id

echo "[localstack-init] DynamoDB initialization complete."

# API Gateway WebSocket initialization
echo "[localstack-init] Initializing API Gateway WebSocket..."

# Helper to create API Gateway WebSocket if it does not exist
create_websocket_api_if_missing() {
  local API_NAME="$1"
  
  # Check if API already exists
  if awslocal apigatewayv2 get-apis --output json | jq -e ".Items[] | select(.Name == \"$API_NAME\")" >/dev/null 2>&1; then
    echo "[localstack-init] WebSocket API '$API_NAME' already exists. Skipping."
    return 0
  fi

  echo "[localstack-init] Creating WebSocket API '$API_NAME'..."
  API_RESPONSE=$(awslocal apigatewayv2 create-api \
    --name "$API_NAME" \
    --protocol-type WEBSOCKET \
    --route-selection-expression '$request.body.action' \
    --description "WebSocket API for real-time comments" \
    --output json)

  if [ $? -eq 0 ]; then
    API_ID=$(echo $API_RESPONSE | jq -r '.ApiId')
    echo "[localstack-init] WebSocket API created with ID: $API_ID"
    
    # Create $connect route
    echo "[localstack-init] Creating \$connect route..."
    awslocal apigatewayv2 create-route \
      --api-id $API_ID \
      --route-key '$connect' \
      --route-response-selection-expression '$default' \
      --output json >/dev/null
    
    # Create $disconnect route
    echo "[localstack-init] Creating \$disconnect route..."
    awslocal apigatewayv2 create-route \
      --api-id $API_ID \
      --route-key '$disconnect' \
      --route-response-selection-expression '$default' \
      --output json >/dev/null
    
    # Create default route for message handling
    echo "[localstack-init] Creating default route..."
    awslocal apigatewayv2 create-route \
      --api-id $API_ID \
      --route-key '$default' \
      --route-response-selection-expression '$default' \
      --output json >/dev/null
    
    # Create deployment
    echo "[localstack-init] Creating deployment..."
    DEPLOY_RESPONSE=$(awslocal apigatewayv2 create-deployment \
      --api-id $API_ID \
      --stage-name dev \
      --description "Development stage for WebSocket API" \
      --output json)
    
    if [ $? -eq 0 ]; then
      DEPLOYMENT_ID=$(echo $DEPLOY_RESPONSE | jq -r '.DeploymentId')
      echo "[localstack-init] Deployment created with ID: $DEPLOYMENT_ID"
      
      # Create stage
      echo "[localstack-init] Creating stage..."
      awslocal apigatewayv2 create-stage \
        --api-id $API_ID \
        --stage-name dev \
        --deployment-id $DEPLOYMENT_ID \
        --description "Development stage" \
        --output json >/dev/null
      
      if [ $? -eq 0 ]; then
        echo "[localstack-init] WebSocket API setup completed successfully!"
        echo "[localstack-init] WebSocket endpoint: ws://localhost:4566"
        echo "[localstack-init] API ID: $API_ID"
      else
        echo "[localstack-init] Warning: Failed to create stage"
      fi
    else
      echo "[localstack-init] Error: Failed to create deployment"
      return 1
    fi
  else
    echo "[localstack-init] Error: Failed to create WebSocket API"
    return 1
  fi
}

# Create WebSocket API
WEBSOCKET_API_NAME="comments-websocket-api"
create_websocket_api_if_missing "$WEBSOCKET_API_NAME"

echo "[localstack-init] LocalStack initialization complete!"
echo "[localstack-init] Services available:"
echo "[localstack-init]   - DynamoDB tables: $POSTS_TABLE, $COMMENTS_TABLE, $FAVORITES_TABLE"
echo "[localstack-init]   - WebSocket API: ws://localhost:4566"
