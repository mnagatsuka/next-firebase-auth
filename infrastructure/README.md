# Infrastructure

This directory contains all Infrastructure as Code (IaC) for the Next.js Firebase Auth project.

## Architecture Overview

The application uses a hybrid infrastructure approach:

- **DynamoDB Local (via Serverless)**: Local DynamoDB for development
- **Serverless Framework**: WebSocket API with TypeScript handlers
- **AWS SAM**: Production deployment of full stack

## Directory Structure

```
infrastructure/
├── aws-sam/           # AWS SAM production deployment
│   ├── template.yml   # Complete infrastructure template
│   ├── samconfig.toml # SAM deployment configuration
│   ├── scripts/       # Deployment scripts
│   └── parameters/    # Environment-specific parameters
└── serverless/        # Serverless Framework WebSocket API
    ├── serverless.yml # WebSocket service configuration
    ├── src/handlers/  # TypeScript WebSocket handlers
    └── tests/         # WebSocket handler tests
```

## Development Setup

### Environment Files
- `serverless/.env.example` → copy to `serverless/.env.development` for local WebSocket development.
- `aws-sam/.env.example` → optional convenience for SAM parameter overrides; SAM reads values via flags, not `.env`.

### Start Serverless WebSocket Service (with DynamoDB Local)
```bash
cd infrastructure/serverless/
pnpm install
pnpm run dev  # Starts on ws://localhost:3001
```

### Start Application Services
```bash
# Backend (from project root)
cd backend/
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (from project root)  
cd frontend/
pnpm dev
```

## Production Deployment

### Recommended: AWS SAM Only (Single Stack)

**AWS SAM is the recommended deployment method** as it manages all resources in a single CloudFormation stack:

```bash
cd infrastructure/aws-sam/

# Build WebSocket handlers
./build-websocket-handlers.sh

# Build and deploy
sam build
sam deploy --guided --parameter-overrides Environment=staging

# For production
sam deploy --guided --parameter-overrides Environment=prod
```

**Benefits:**
- ✅ Single deployment pipeline
- ✅ All resources in one CloudFormation stack  
- ✅ Consistent tagging and resource management
- ✅ Unified rollback and monitoring
- ✅ No tool version conflicts

### Alternative: Serverless Framework (Development Only)

The Serverless Framework setup is kept for **local development only**:

```bash
cd infrastructure/serverless/
pnpm run dev  # Local WebSocket server for development
```

**Note:** For production, use AWS SAM deployment above instead of Serverless Framework to avoid resource conflicts.

## Infrastructure Components

### AWS SAM Template
The consolidated `aws-sam/template.yml` includes:

- **FastAPI Backend**: Lambda with Web Adapter
- **DynamoDB Tables**: Posts, Comments, Favorites, WebSocket Connections
- **WebSocket API**: Real-time communication
- **HTTP API Gateway**: REST endpoints
- **CloudWatch Logs**: Monitoring and debugging
- **IAM Roles**: Least privilege permissions

### Serverless WebSocket API
- **TypeScript handlers** for connect/disconnect/broadcast
- **Development server** with serverless-offline
- **Comprehensive testing** with Vitest
- **Production deployment** to AWS API Gateway V2

### DynamoDB Local (via Serverless)
- **DynamoDB Local** started automatically by `serverless offline`
- **Tables auto-created** from `resources` with `migrate: true`

## Environment Configuration

### Development
- DynamoDB Local (via Serverless): `http://websocket:8002` from Docker network, or `http://localhost:8002` if exposed
- Serverless WebSocket: `ws://localhost:3001`
- FastAPI Backend: `http://localhost:8000`
- Next.js Frontend: `http://localhost:3000`

### Production
Environment variables managed by AWS SAM template:
- DynamoDB table names with environment prefixes
- WebSocket API URLs with proper stages
- CORS configuration by environment

## Testing

### Serverless WebSocket Tests
```bash
cd infrastructure/serverless/
pnpm test                    # Run once
pnpm test:watch             # Watch mode
pnpm test:coverage          # With coverage
```

### Infrastructure Validation
```bash
cd infrastructure/aws-sam/
sam validate                 # Validate template
sam local start-api         # Test locally
```

## Monitoring

### CloudWatch Logs
- `/aws/lambda/{stack-name}-api` - FastAPI application
- `/aws/lambda/{stack-name}-websocket-*` - WebSocket handlers

### Metrics
- API Gateway request metrics
- Lambda function performance
- DynamoDB operation metrics

## Cost Optimization

- **DynamoDB**: Pay-per-request billing
- **Lambda**: Pay-per-invocation with efficient memory allocation
- **API Gateway**: Pay-per-request with proper throttling
- **WebSocket**: Automatic connection scaling

## Security

- **IAM Roles**: Least privilege access
- **CORS**: Environment-specific origins
- **VPC**: Optional VPC configuration for production
- **Encryption**: At-rest and in-transit encryption enabled

## Troubleshooting

### Common Issues
1. **WebSocket Failures**: Check Serverless service on port 3001
2. **SAM Deployment**: Validate template and check AWS credentials
3. **Permission Errors**: Review IAM policies in template

### Debug Commands
```bash
# Test WebSocket HTTP endpoint
curl -X POST http://localhost:3001/development/broadcast/comments \
  -H "Content-Type: application/json" \
  -d '{"type":"test","data":{}}'

# WebSocket connection test
wscat -c ws://localhost:3001

# SAM local testing
sam local start-api --port 3001
```

## Migration Benefits

✅ **Centralized Infrastructure**: All IaC in one location  
✅ **Clean Separation**: Application code vs Infrastructure code  
✅ **Team Collaboration**: Clear ownership boundaries  
✅ **Production Ready**: Comprehensive AWS deployment  
✅ **Cost Effective**: No LocalStack Pro dependency  
✅ **Type Safety**: TypeScript WebSocket handlers  
✅ **Scalable**: Auto-scaling AWS services
