# 14. Deployment & Operations

This section covers **simple deployment** for Python + FastAPI backend projects using **AWS SAM**, **Lambda Web Adapter**, and **GitHub Actions**. It follows the established tech stack: Python 3.13, FastAPI, Firebase Auth, DynamoDB, and S3.

The strategy emphasizes **straightforward deployment workflows** using SAM for serverless deployment with Lambda Web Adapter.


## 1. Deployment Overview

Simple deployment workflow using AWS SAM and Lambda Web Adapter:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Build     │    │   Deploy    │    │   Verify    │
│   with SAM  │───▶│   to AWS    │───▶│   Health    │
│             │    │             │    │   Check     │
└─────────────┘    └─────────────┘    └─────────────┘
```

**Deployment Methods:**
1. **Local deployment** using SAM CLI
2. **GitHub Actions** for automated deployment

**Rules:**

* Use AWS Lambda Web Adapter for FastAPI compatibility.
* Deploy with environment-specific configurations.
* Use simple SAM commands and GitHub Actions.


## 2. SAM Template Configuration

### Basic SAM Template

```yaml
# backend/template.yml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: FastAPI Backend with Lambda Web Adapter

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.13
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        LOG_LEVEL: !If [IsProd, 'INFO', 'DEBUG']
        AWS_LAMBDA_EXEC_WRAPPER: /opt/bootstrap
        PORT: 8000

Conditions:
  IsProd: !Equals [!Ref Environment, 'prod']

Resources:
  # Lambda Web Adapter Layer
  LambdaWebAdapterLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub '${AWS::StackName}-lambda-web-adapter'
      Description: Lambda Web Adapter
      ContentUri: https://github.com/awslabs/aws-lambda-web-adapter/releases/latest/download/lambda-adapter.zip
      CompatibleRuntimes:
        - python3.13

  # FastAPI Function
  FastAPIFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub '${AWS::StackName}-api'
      CodeUri: .
      Handler: run.sh
      Runtime: provided.al2023
      Layers:
        - !Ref LambdaWebAdapterLayer
      Environment:
        Variables:
          DYNAMODB_TABLE: !Ref DynamoDBTable
          S3_BUCKET: !Ref S3Bucket
          FIREBASE_PROJECT_ID: !Sub '${Environment}-firebase-project'
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY

  # DynamoDB Table
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${AWS::StackName}-main'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: sk
              KeyType: HASH
            - AttributeName: pk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  # S3 Bucket
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-uploads'
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders: ['*']
            AllowedMethods: [GET, PUT, POST, DELETE]
            AllowedOrigins: 
              - !If [IsProd, 'https://yourdomain.com', '*']

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub 'https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com'
  
  DynamoDBTable:
    Description: DynamoDB table name
    Value: !Ref DynamoDBTable
    
  S3Bucket:
    Description: S3 bucket name
    Value: !Ref S3Bucket
```

### SAM Configuration

```toml
# backend/samconfig.toml
version = 0.1

[default.global.parameters]
stack_name = "fastapi-backend"

[default.build.parameters]
cached = true

[default.deploy.parameters]
capabilities = "CAPABILITY_IAM"
confirm_changeset = false
resolve_s3 = true
region = "us-east-1"

# Development
[dev.deploy.parameters]
stack_name = "fastapi-backend-dev"
parameter_overrides = ["Environment=dev"]

# Staging
[staging.deploy.parameters]
stack_name = "fastapi-backend-staging"
parameter_overrides = ["Environment=staging"]

# Production
[prod.deploy.parameters]
stack_name = "fastapi-backend-prod"
parameter_overrides = ["Environment=prod"]
confirm_changeset = true
```

**Rules:**

* Use Lambda Web Adapter layer for FastAPI compatibility.
* Use HttpApi for better performance and lower cost.
* Configure environment-specific parameters.


## 3. FastAPI Application Setup

### Main Application

```python
# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import api_router
from shared.config import get_settings

settings = get_settings()

app = FastAPI(
    title="FastAPI Backend",
    description="Backend API with Clean Architecture",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS middleware
if not settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }

# Include API routes
app.include_router(api_router)
```

### Run Script for Lambda Web Adapter

```bash
#!/bin/bash
# backend/run.sh
exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Configuration

*Configuration setup is covered in detail in [04_configuration.md](./04_configuration.md). Use Pydantic Settings for environment-specific configurations.*

### Dependencies Configuration

```toml
# backend/pyproject.toml
[project]
name = "fastapi-backend"
version = "1.0.0"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "boto3>=1.34.0",
    "firebase-admin>=6.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Rules:**

* Use Lambda Web Adapter with uvicorn for FastAPI compatibility.
* Configure environment-specific settings with Pydantic.
* Follow the established Clean Architecture structure.


## 4. Local Deployment Commands

### Basic Commands

```bash
# Navigate to backend directory
cd backend

# Make run script executable
chmod +x run.sh

# Build
sam build

# Deploy to different environments
sam deploy --config-env dev
sam deploy --config-env staging
sam deploy --config-env prod
```

### Deployment Script

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENV=${1:-dev}
echo "Deploying to environment: $ENV"

cd backend

# Make run script executable
chmod +x run.sh

# Build and deploy
sam build
sam deploy --config-env $ENV

# Get outputs
STACK_NAME="fastapi-backend-$ENV"
API_URL=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

echo "Deployment completed!"
echo "API URL: $API_URL"

# Health check
echo "Running health check..."
if curl -f "$API_URL/health" > /dev/null 2>&1; then
  echo "✓ Health check passed"
else
  echo "✗ Health check failed"
  exit 1
fi
```

### Makefile

```makefile
# Makefile
.PHONY: build deploy-dev deploy-staging deploy-prod local clean

# Build SAM application
build:
	cd backend && chmod +x run.sh && sam build

# Deploy to environments
deploy-dev: build
	cd backend && sam deploy --config-env dev

deploy-staging: build
	cd backend && sam deploy --config-env staging

deploy-prod: build
	cd backend && sam deploy --config-env prod

# Local development
local: build
	cd backend && sam local start-api --port 3001

# Clean build artifacts
clean:
	cd backend && rm -rf .aws-sam
```

**Rules:**

* Make run.sh executable before building.
* Use environment-specific configurations.
* Include health checks after deployment.


## 5. GitHub Actions Deployment

### Simple Deployment Workflow

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches:
      - main        # Deploy to staging
      - production  # Deploy to production
    paths: ['backend/**']
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'dev'
        type: choice
        options:
        - dev
        - staging
        - prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ steps.env.outputs.environment }}
    defaults:
      run:
        working-directory: backend
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Setup SAM CLI
        uses: aws-actions/setup-sam@v2

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Determine environment
        id: env
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/production" ]; then
            echo "environment=prod" >> $GITHUB_OUTPUT
          else
            echo "environment=staging" >> $GITHUB_OUTPUT
          fi

      - name: Make run script executable
        run: chmod +x run.sh

      - name: SAM build
        run: sam build

      - name: SAM deploy
        run: sam deploy --config-env ${{ steps.env.outputs.environment }}

      - name: Get API URL
        id: url
        run: |
          STACK_NAME="fastapi-backend-${{ steps.env.outputs.environment }}"
          URL=$(aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
            --output text)
          echo "api-url=$URL" >> $GITHUB_OUTPUT

      - name: Health check
        run: |
          echo "Testing: ${{ steps.url.outputs.api-url }}"
          curl -f ${{ steps.url.outputs.api-url }}/health
```

### GitHub Environment Configuration

Create GitHub environments with secrets:

**Development Environment:**
- `AWS_ACCESS_KEY_ID`: Dev AWS access key
- `AWS_SECRET_ACCESS_KEY`: Dev AWS secret key

**Staging Environment:**
- `AWS_ACCESS_KEY_ID`: Staging AWS access key
- `AWS_SECRET_ACCESS_KEY`: Staging AWS secret key

**Production Environment:**
- `AWS_ACCESS_KEY_ID`: Prod AWS access key
- `AWS_SECRET_ACCESS_KEY`: Prod AWS secret key

**Rules:**

* Use GitHub environments for secret management.
* Deploy automatically on branch pushes.
* Include health checks in deployment workflow.


## 6. Firebase Auth Integration

*Firebase Auth integration patterns are covered in detail in [09_infrastructure.md](./09_infrastructure.md). Use the established authentication adapters for token verification and user management.*

**Rules:**

* Use Firebase Admin SDK for token verification.
* Implement proper error handling for authentication.
* Use FastAPI Security for consistent auth patterns.


## 7. DynamoDB Integration

*DynamoDB repository patterns and single-table design are covered in detail in [16_data-modeling.md](./16_data-modeling.md) and [09_infrastructure.md](./09_infrastructure.md). Use the established repository patterns for data access.*

**Rules:**

* Use repository pattern for data access.
* Follow DynamoDB single-table design.
* Implement proper error handling.


## 8. Testing & Verification

### Local Testing

```bash
# Test locally with SAM
sam local start-api --port 3000

# Test endpoints
curl http://localhost:3000/health
curl http://localhost:3000/users
```

### Post-Deployment Testing

```python
# tests/smoke/test_deployment.py
import os
import requests
import pytest

API_URL = os.getenv("API_URL")

@pytest.mark.skipif(not API_URL, reason="API_URL not set")
def test_health_endpoint():
    """Test health endpoint."""
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.skipif(not API_URL, reason="API_URL not set")  
def test_protected_endpoint():
    """Test protected endpoint requires auth."""
    response = requests.get(f"{API_URL}/users")
    assert response.status_code == 401  # Unauthorized without token
```

**Rules:**

* Test locally before deploying.
* Run smoke tests after deployment.
* Verify authentication endpoints work correctly.


## 9. Monitoring & Troubleshooting

### CloudWatch Logs

```bash
# View function logs
aws logs tail /aws/lambda/fastapi-backend-dev-api --follow

# Check specific log group
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/fastapi-backend"
```

### Common Issues

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name fastapi-backend-dev

# Test Lambda function directly
aws lambda invoke \
  --function-name fastapi-backend-dev-api \
  --payload '{}' \
  response.json

# Check function configuration
aws lambda get-function-configuration \
  --function-name fastapi-backend-dev-api
```

**Rules:**

* Monitor CloudWatch logs for errors.
* Use CloudFormation events for deployment debugging.
* Test Lambda functions directly when troubleshooting.


## 10. Quick Reference

### Deployment Commands

```bash
# Local development
make local                    # Start local API
make build                    # Build SAM application

# Deploy to environments  
make deploy-dev              # Deploy to development
make deploy-staging          # Deploy to staging
make deploy-prod             # Deploy to production

# Manual deployment
scripts/deploy.sh dev        # Deploy to specific environment
```

### Required Files

```
backend/
├── template.yml           # SAM template
├── samconfig.toml          # SAM configuration
├── run.sh                  # Lambda Web Adapter run script
├── pyproject.toml          # Python dependencies
├── main.py                 # FastAPI application
└── shared/config.py        # Configuration settings
```

### GitHub Actions Triggers

- **Push to `main`** → Deploy to staging
- **Push to `production`** → Deploy to production
- **Manual trigger** → Deploy to chosen environment

**Rules:**

* Keep deployment simple with clear commands.
* Use Lambda Web Adapter for FastAPI compatibility.
* Follow established Clean Architecture patterns.
* Monitor deployments with health checks.