# 14. Deployment & Operations

This document outlines the deployment process for the backend service. The backend is a FastAPI application, containerized for local development and deployed as a serverless application on AWS using the AWS Serverless Application Model (SAM).

**The current deployment process is manual.** All deployments to AWS environments must be performed from a developer's local machine using the AWS SAM CLI.

For detailed, step-by-step instructions on setting up your environment for deployment, refer to the main [DEPLOYMENT.md](../../../DEPLOYMENT.md) guide.

## 1. Deployment Environments

The project uses three primary environments, which are configured in `infrastructure/aws-sam/samconfig.toml`:

-   **Development (`development`)**: A shared cloud environment for development and feature testing.
-   **Staging (`staging`)**: A production-like environment for integration testing and QA.
-   **Production (`production`)**: The live environment for end-users.

## 2. Manual Deployment Workflow

Deployments are performed manually using the AWS SAM CLI. This gives developers direct control over the deployment process.

**Prerequisites:**
- AWS CLI and SAM CLI installed and configured.
- Docker running on your machine.
- You have been granted the necessary IAM permissions for deployment.

**Deployment Steps:**

1.  **Navigate to the SAM directory:**
    ```bash
    cd infrastructure/aws-sam/
    ```

2.  **Build the WebSocket handlers (first time or if they change):**
    ```bash
    ./build-websocket-handlers.sh
    ```

3.  **Build the SAM application:**
    ```bash
    sam build
    ```

4.  **Deploy to the desired environment:**
    ```bash
    # Deploy to staging
    sam deploy --config-env staging

    # Deploy to production (requires confirmation)
    sam deploy --config-env production
    ```

> For a complete guide on manual deployment, including handling parameter overrides for production, see [DEPLOYMENT.md](../../../DEPLOYMENT.md).

## 3. Local vs. Deployed Environment

It's important to understand the differences between the local development environment and the deployed AWS environment.

-   **Local (Docker Compose)**: Runs the FastAPI app in a standard Python container. By default, it uses an **in-memory repository** for data, meaning data is lost on restart.
-   **Deployed (AWS SAM)**: Runs the FastAPI app inside an **AWS Lambda function** using the Lambda Web Adapter. It connects to managed AWS services, including **DynamoDB** for persistent data storage.

The data repository can be switched via the `APP_REPOSITORY_PROVIDER` environment variable (`memory` or `dynamodb`).

## 4. Post-Deployment Verification

After every deployment, it is crucial to verify that the service is running correctly.

-   Perform a health check by accessing the `/api/health` endpoint of the newly deployed API.
-   The API URL can be found in the outputs of the `sam deploy` command or in the AWS CloudFormation console.
-   Run any relevant smoke tests to ensure core functionality is working as expected.
