# Backend Deployment Guideline (AWS SAM)

This guide provides instructions for deploying the backend service (FastAPI application) using the AWS Serverless Application Model (SAM).

## 1. Architecture Overview

The backend is a full-stack serverless application with FastAPI backend and WebSocket support, deployed using container images and Node.js Lambda functions.

-   **Compute**: 
    - AWS Lambda with Docker container images (ECR) for FastAPI backend
    - Node.js 20.x Lambda functions for WebSocket handlers
-   **API Endpoints**: 
    - **Lambda Function URL** for direct FastAPI REST API access
    - **HTTP API Gateway v2** for WebSocket broadcasting endpoint (`/broadcast/comments`)
    - **WebSocket API Gateway v2** for real-time communication
-   **Database**: Amazon DynamoDB tables for Posts, Comments, Favorites, and WebSocket connections
-   **Real-time Communication**: Dedicated WebSocket handlers (Connect/Disconnect/Default/Broadcast) manage real-time features
-   **Deployment**: Two-template strategy using AWS SAM for better separation of concerns

## 2. Prerequisites

Before deploying, ensure you have the following installed and configured:

-   **AWS CLI**: Authenticated with an IAM user possessing permissions to deploy AWS CloudFormation, Lambda, DynamoDB, ECR, and related resources.
-   **AWS SAM CLI**: For building and deploying the serverless application.
-   **Docker**: Required for building Lambda container images and pushing to ECR.
-   **Python & `uv`**: For running local scripts and managing dependencies.
-   **pnpm**: For managing WebSocket handler dependencies (Node.js TypeScript project).

## 3. Environments

The project is configured for three distinct environments, managed in `infrastructure/aws-sam/samconfig.toml`:

-   `development`: For feature development and testing.
-   `staging`: A production-like environment for QA and integration testing.
-   `production`: The live environment for end-users.

Each environment has its own stack name, parameter overrides, and tags, ensuring complete isolation.

## 4. Deployment Steps

All deployments are performed **manually** from your local machine using SAM's integrated Docker workflow.

### Prerequisites Setup

1.  **Clean Up Existing Stack (if upgrading)**

    If you have an existing stack from the Lambda Web Adapter architecture, delete it first:

    ```bash
    # Check existing stacks
    aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --region ap-northeast-1
    
    # Delete old stack (replace with your actual stack name)
    aws cloudformation delete-stack --stack-name blogapp-staging --region ap-northeast-1
    
    # Wait for deletion to complete
    aws cloudformation wait stack-delete-complete --stack-name blogapp-staging --region ap-northeast-1
    
    # Verify deletion
    aws cloudformation describe-stacks --stack-name blogapp-staging --region ap-northeast-1
    # Should return: "Stack does not exist"
    ```

    **⚠️ Important**: This will delete all data in DynamoDB tables. Export data first if needed.

2.  **Configure AWS Credentials**

    **Step 1: Get AWS credentials from your AWS account**
    - Log in to AWS Console → IAM → Users → [Your user] → Security credentials
    - Create Access Keys if you don't have them
    - Note down: Access Key ID and Secret Access Key

    **Step 2: Configure credentials (choose one method):**

    **Option A: Default profile (simplest)**
    ```bash
    aws configure
    # Enter when prompted:
    # AWS Access Key ID: [your-access-key-id]
    # AWS Secret Access Key: [your-secret-key]
    # Default region name: ap-northeast-1
    # Default output format: json
    ```

    **Option B: Named profiles (recommended for multiple environments)**
    ```bash
    # Configure staging profile
    aws configure --profile staging
    # Enter credentials for staging environment
    
    # Configure production profile  
    aws configure --profile production
    # Enter credentials for production environment
    ```

    **Option C: Environment variables (temporary session)**
    ```bash
    export AWS_ACCESS_KEY_ID=your_access_key_id
    export AWS_SECRET_ACCESS_KEY=your_secret_access_key
    export AWS_DEFAULT_REGION=ap-northeast-1
    ```

    **Step 3: Verify credentials work**
    ```bash
    # Test default profile
    aws sts get-caller-identity --region ap-northeast-1
    
    # Test named profile
    aws sts get-caller-identity --profile staging --region ap-northeast-1
    
    # Should return your AWS account info (Account ID, User ARN, etc.)
    ```

    **Required IAM Permissions:**
    Your AWS user needs these permissions:
    - CloudFormation: Full access
    - Lambda: Full access  
    - ECR: Full access
    - DynamoDB: Full access
    - API Gateway: Full access
    - IAM: Pass role permissions
    - CloudWatch Logs: Create log groups

3.  **Navigate to the SAM Directory**

    ```bash
    cd infrastructure/aws-sam/
    ```

### Deployment Process

The deployment uses a **two-template strategy** for better separation of concerns:

4.  **Create ECR Repository (One-time setup)**

    Deploy the ECR template first to create container repositories:

    ```bash
    # For staging environment
    sam deploy --config-env ecr-staging --profile staging
    
    # For production environment  
    sam deploy --config-env ecr-production --profile production
    
    # Without profiles (using default credentials)
    sam deploy --config-env ecr-staging
    ```

    This creates a separate CloudFormation stack (e.g., `blogapp-staging-ecr`) containing only the ECR repository.

5.  **Build WebSocket Handlers (if changed)**

    Only run this if TypeScript WebSocket handlers have changed:

    ```bash
    ./build-websocket-handlers.sh
    ```

    This script:
    - Installs dependencies with `pnpm install --production`
    - Prepares handlers for SAM's automatic TypeScript compilation

6.  **Build Application Components**

    This builds both WebSocket handlers (TypeScript) and Docker images:

    ```bash
    # With cache
    sam build

    # Without cache
    sam build --no-cache
    ```

    SAM will:
    - Compile TypeScript WebSocket handlers using esbuild
    - Build the Docker image using `backend/Dockerfile.lambda` 
    - Automatically authenticate with ECR
    - Push the image to the ECR repository (referenced via SSM parameter)
    - Tag the image as `:latest` for Lambda function deployment

7.  **Deploy Application**

    Deploy the main application stack:

    ```bash
    # Deploy to staging
    sam deploy --config-env staging --profile staging
    
    # Deploy to production
    sam deploy --config-env production --profile production
    
    # Without profiles
    sam deploy --config-env staging
    ```

### Quick Commands Summary

**Complete first-time setup for staging:**
```bash
cd infrastructure/aws-sam

# Step 1: Create ECR repository (one-time)
sam deploy --config-env ecr-staging --profile staging

# Step 2: Build and deploy application
./build-websocket-handlers.sh  # Only if WebSocket handlers changed
sam build
sam deploy --config-env staging --profile staging
```

**Subsequent code updates:**
```bash
cd infrastructure/aws-sam
sam build  # REQUIRED: Builds TypeScript handlers and pushes Docker image to ECR
sam deploy --config-env staging --profile staging
```

**Production deployment:**
```bash
# First time: Create ECR + Deploy
sam deploy --config-env ecr-production --profile production
sam build
sam deploy --config-env production --profile production

# Updates: Build + Deploy
sam build
sam deploy --config-env production --profile production
```

**Without AWS profiles (using default credentials):**
```bash
# First time
sam deploy --config-env ecr-staging
sam build  
sam deploy --config-env staging

# Updates
sam build
sam deploy --config-env staging
```

## 5. Architecture: Two-Template Strategy

This deployment uses two separate CloudFormation templates for better management:

### **Template 1: ECR Setup (`template-ecr.yml`)**
- **Purpose**: Creates ECR repository for Docker images
- **Stack Name**: `blogapp-{environment}-ecr` (e.g., `blogapp-staging-ecr`)
- **Resources**: ECR repository with lifecycle policies and image scanning
- **When to deploy**: Once per environment (or when ECR configuration changes)

### **Template 2: Main Application (`template.yml`)**  
- **Purpose**: Deploys all application resources (Lambda, DynamoDB, API Gateway, etc.)
- **Stack Name**: `blogapp-{environment}` (e.g., `blogapp-staging`)
- **Docker Integration**: References ECR repository from Template 1 via CloudFormation exports
- **When to deploy**: Every code update or infrastructure change

### **Benefits of This Approach:**
- ✅ **Separation of concerns** - ECR lifecycle separate from application
- ✅ **Faster deployments** - Don't recreate ECR repository every time  
- ✅ **Better error handling** - ECR issues don't block application updates
- ✅ **SAM automation** - `sam build` automatically handles Docker build/push
- ✅ **Clean workflows** - Clear distinction between setup and updates

## 6. Configuration

### Deployment Parameters

Environment-specific parameters are defined in `infrastructure/aws-sam/samconfig.toml`:

#### **ECR Template Parameters (`ecr-{environment}` sections):**
-   `Environment`: Environment name (`development`, `staging`, `production`)
-   `template_file`: Points to `template-ecr.yml`

#### **Main Template Parameters (`{environment}` sections):**  
-   `Environment`: The name of the environment (`development`, `staging`, or `production`)
-   `AllowedOrigins`: CORS origins for WebSocket broadcast endpoint (REST API uses wildcard)
-   `FirebaseProjectId`: Firebase project ID for authentication

#### **Template Files:**
-   `template-ecr.yml`: ECR repository setup only
-   `template.yml`: Main application (imports ECR repository URI)

### Application Environment Variables

The Lambda functions' environment variables are set within `template.yml` and are automatically configured during deployment:

#### FastAPI Backend Environment Variables:
-   `REPOSITORY_PROVIDER`: Set to `dynamodb` for all deployed environments
-   `APP_DYNAMODB_TABLE_POSTS`: DynamoDB Posts table name (dynamically generated)
-   `APP_DYNAMODB_TABLE_COMMENTS`: DynamoDB Comments table name (dynamically generated)  
-   `APP_DYNAMODB_TABLE_FAVORITES`: DynamoDB Favorites table name (dynamically generated)
-   `APP_SERVERLESS_WEBSOCKET_ENDPOINT`: HTTP API endpoint for WebSocket broadcasting
-   `FIREBASE_PROJECT_ID`: Injected from SAM deployment parameters
-   `APP_ENVIRONMENT`: Environment name (development/staging/production)

#### WebSocket Handler Environment Variables:
-   `DYNAMODB_CONNECTIONS_TABLE`: WebSocket connections table name
-   `WEBSOCKET_API_ENDPOINT`: WebSocket API Gateway endpoint URL
-   `LOG_LEVEL`: Configurable logging level (DEBUG for dev, INFO for production)
-   `FIREBASE_PROJECT_ID`: Firebase project ID for authentication

## 6. Post-Deployment Verification

1.  **Get API Endpoints**

    After a successful deployment, SAM will output multiple endpoint URLs:

    ```bash
    # Get FastAPI Function URL endpoint
    aws cloudformation describe-stacks \
      --stack-name blogapp-<environment> \
      --region ap-northeast-1 \
      --query "Stacks[0].Outputs[?OutputKey=='FunctionUrlEndpoint'].OutputValue" \
      --output text

    # Get WebSocket URL
    aws cloudformation describe-stacks \
      --stack-name blogapp-<environment> \
      --region ap-northeast-1 \
      --query "Stacks[0].Outputs[?OutputKey=='WebSocketURL'].OutputValue" \
      --output text

    # Get WebSocket Broadcast API URL
    aws cloudformation describe-stacks \
      --stack-name blogapp-<environment> \
      --region ap-northeast-1 \
      --query "Stacks[0].Outputs[?OutputKey=='BroadcastApiUrl'].OutputValue" \
      --output text
    ```

2.  **Perform Health Checks**

    Test the FastAPI backend:
    ```bash
    # Replace <your-function-url> with the FastAPI Function URL
    curl <your-function-url>/health
    ```

    Expected response:
    ```json
    {"status":"healthy","message":"API is running"}
    ```

    Test WebSocket connectivity using a WebSocket client or browser developer tools.

3.  **Check CloudWatch Logs**

    Monitor logs for different components:

    ```bash
    # FastAPI backend logs
    aws logs tail /aws/lambda/<stack-name>-api --follow --region ap-northeast-1

    # WebSocket handler logs
    aws logs tail /aws/lambda/<stack-name>-websocket-connect --follow --region ap-northeast-1
    aws logs tail /aws/lambda/<stack-name>-websocket-broadcast --follow --region ap-northeast-1

    # API Gateway logs
    aws logs tail /aws/apigateway/<stack-name>-http-api --follow --region ap-northeast-1
    aws logs tail /aws/apigateway/<stack-name>-websocket-api --follow --region ap-northeast-1
    ```

## 7. Architecture Components Detail

### Lambda Functions

#### FastAPI Backend (`BlogAPIFunction`)
- **Image**: Docker container using ECR (references via SSM parameter)  
- **Runtime**: Python 3.11 with FastAPI + uv package manager
- **Integration**: Lambda Function URL for direct HTTP access
- **Environment**: DynamoDB table names, Firebase project ID, WebSocket broadcast endpoint

#### WebSocket Handlers (Node.js 20.x + AWS SDK v3)
- **`WebSocketConnectFunction`**: Handles new WebSocket connections, stores connection info in DynamoDB
- **`WebSocketDisconnectFunction`**: Cleans up disconnected connections from DynamoDB  
- **`WebSocketDefaultFunction`**: Processes incoming WebSocket messages (echo functionality)
- **`WebSocketBroadcastFunction`**: HTTP-triggered function for broadcasting messages to all connected clients

### API Gateways

#### HTTP API Gateway v2 (`BlogHttpApi`)
- **Purpose**: Serves the WebSocket broadcasting endpoint
- **Route**: `POST /broadcast/comments` → WebSocketBroadcastFunction
- **CORS**: Configurable per environment via `AllowedOrigins` parameter

#### WebSocket API Gateway v2 (`WebSocketAPI`)  
- **Routes**:
  - `$connect` → WebSocketConnectFunction
  - `$disconnect` → WebSocketDisconnectFunction  
  - `$default` → WebSocketDefaultFunction
- **Stage**: Named after environment (development/staging/production)

### DynamoDB Tables

All tables use **pay-per-request billing** and have **PITR disabled** for cost optimization:

- **PostsTable**: Blog posts (`id` as primary key)
- **CommentsTable**: Comments (`id` as primary key)  
- **FavoritesTable**: User favorites (composite key: `user_id` + `post_id`)
- **WebSocketConnectionsTable**: Active connections (`connectionId` as primary key, TTL enabled)

### Docker Configuration

The FastAPI backend uses a production-optimized Dockerfile (`backend/Dockerfile.lambda`):
- Base image: `public.ecr.aws/lambda/python:3.11`
- Package manager: `uv` (faster than pip)  
- Dependencies: FastAPI, Uvicorn, Pydantic, Firebase Admin, Boto3, requests, python-multipart
- Handler: `app.main.app` (ASGI application)
- ECR Integration: Image URI resolved via SSM parameter `/blogapp/${Environment}/ecr-repository-uri`

### WebSocket Handler Structure

The WebSocket handlers are organized with shared utilities:

```
websocket-handlers/
├── connect.ts          # Connection handler
├── disconnect.ts       # Disconnection handler  
├── default.ts          # Default message handler
├── broadcast.ts        # Broadcasting handler
├── shared/
│   ├── types.ts        # TypeScript interfaces
│   ├── clients.ts      # AWS SDK v3 clients
│   ├── utils.ts        # Helper functions
│   └── broadcast-service.ts  # Broadcasting logic
├── package.json        # Node.js dependencies
└── tsconfig.json       # TypeScript configuration
```

Key features:
- **Shared utilities** eliminate code duplication
- **Type safety** with comprehensive TypeScript interfaces
- **Chunked broadcasting** prevents API throttling
- **Stale connection cleanup** with proper error handling
- **Structured logging** with configurable log levels

## 8. Troubleshooting

### Common Issues

#### 1. **Error: "Source image does not exist"**

```
CREATE_FAILED: Source image 909481621682.dkr.ecr.ap-northeast-1.amazonaws.com/blogapp-staging-ecr-api:latest does not exist
```

**Cause**: The ECR repository was created but no Docker image has been pushed yet.

**Solution**: Run `sam build` first to build and push the Docker image, then deploy:
```bash
# Step 1: Build and push Docker image
sam build

sam build --no-cache

# Step 2: Deploy application
sam deploy --config-env staging --profile staging
```

#### 2. **Error: "ECR repository already exists"**

**Cause**: Conflicting ECR repositories - both auto-created by SAM and from ECR template.

**Solution**: Delete the auto-created ECR repository and use only the ECR template:
```bash
# List repositories to find the conflicting one
aws ecr describe-repositories --profile staging --region ap-northeast-1

# Delete the auto-created repository (usually has a random ID)
aws ecr delete-repository --repository-name <auto-created-repo-name> --force --profile staging --region ap-northeast-1
```

#### 3. **Error: "Parameters: [ssm:/blogapp/staging/ecr-repository-uri] cannot be found"**

**Cause**: ECR template hasn't been deployed yet.

**Solution**: Deploy ECR template first:
```bash
sam deploy --config-env ecr-staging --profile staging
```

#### 4. **Build Failure: Docker Permission Issues**

**Cause**: Docker daemon not running or permission issues.

**Solution**: 
```bash
# Start Docker daemon
sudo systemctl start docker  # Linux
# or Docker Desktop on macOS/Windows

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Logout and login again
```

### Stack Cleanup

If deployment fails and you need to start fresh:

```bash
# Delete failed stacks
aws cloudformation delete-stack --stack-name blogapp-staging --profile staging --region ap-northeast-1

# Delete companion stacks (auto-created by SAM)
aws cloudformation list-stacks --profile staging --region ap-northeast-1 --stack-status-filter ROLLBACK_COMPLETE | grep CompanionStack
aws cloudformation delete-stack --stack-name <companion-stack-name> --profile staging --region ap-northeast-1

# Wait for deletion to complete before retrying
aws cloudformation wait stack-delete-complete --stack-name blogapp-staging --profile staging --region ap-northeast-1
```
