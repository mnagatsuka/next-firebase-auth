#!/bin/bash

# LocalStack DynamoDB Table Initialization Script
# This script creates all required DynamoDB tables for the Next.js Firebase Auth application
# Based on table definitions from infrastructure/serverless/serverless.yml

set -e

echo "🚀 Initializing DynamoDB tables in LocalStack..."

# LocalStack endpoint
LOCALSTACK_ENDPOINT="http://localhost:4566"
AWS_REGION="ap-northeast-1"

# Set fake AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="$AWS_REGION"

# Function to create table if it doesn't exist
create_table_if_not_exists() {
    local table_name="$1"
    local table_definition="$2"
    
    echo "📋 Checking if table '$table_name' exists..."
    
    if aws dynamodb describe-table \
        --endpoint-url "$LOCALSTACK_ENDPOINT" \
        --region "$AWS_REGION" \
        --table-name "$table_name" \
        >/dev/null 2>&1; then
        echo "✅ Table '$table_name' already exists, skipping..."
    else
        echo "🔧 Creating table '$table_name'..."
        eval "$table_definition"
        echo "✅ Table '$table_name' created successfully!"
    fi
}

# Posts Table
posts_table='aws dynamodb create-table \
    --endpoint-url "$LOCALSTACK_ENDPOINT" \
    --region "$AWS_REGION" \
    --table-name "posts" \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST'

# Comments Table
comments_table='aws dynamodb create-table \
    --endpoint-url "$LOCALSTACK_ENDPOINT" \
    --region "$AWS_REGION" \
    --table-name "comments" \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST'

# Favorites Table (composite key: user_id + post_id)
favorites_table='aws dynamodb create-table \
    --endpoint-url "$LOCALSTACK_ENDPOINT" \
    --region "$AWS_REGION" \
    --table-name "favorites" \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=post_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=post_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST'

# WebSocket Connections Table (with TTL)
connections_table='aws dynamodb create-table \
    --endpoint-url "$LOCALSTACK_ENDPOINT" \
    --region "$AWS_REGION" \
    --table-name "blogapp-websocket-connections-development" \
    --attribute-definitions AttributeName=connectionId,AttributeType=S \
    --key-schema AttributeName=connectionId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST'

# Create all tables
create_table_if_not_exists "posts" "$posts_table"
create_table_if_not_exists "comments" "$comments_table"
create_table_if_not_exists "favorites" "$favorites_table"
create_table_if_not_exists "blogapp-websocket-connections-development" "$connections_table"

# Configure TTL for connections table
echo "⏰ Configuring TTL for WebSocket connections table..."
aws dynamodb update-time-to-live \
    --endpoint-url "$LOCALSTACK_ENDPOINT" \
    --region "$AWS_REGION" \
    --table-name "blogapp-websocket-connections-development" \
    --time-to-live-specification Enabled=true,AttributeName=ttl \
    >/dev/null 2>&1 || echo "⚠️  TTL configuration may have failed (this is often okay in LocalStack)"

# List all tables for verification
echo ""
echo "📊 Listing all created tables:"
aws dynamodb list-tables \
    --endpoint-url "$LOCALSTACK_ENDPOINT" \
    --region "$AWS_REGION" \
    --output table

echo ""
echo "🎉 DynamoDB initialization completed successfully!"
echo "📍 Tables are available at: $LOCALSTACK_ENDPOINT"
echo "🔍 You can now use the DynamoDB repository provider in your backend application."
