# Backend Deployment

This directory contains all deployment configurations and scripts for the Blog API backend.

## 📁 Directory Structure

```
backend/deploy/
├── README.md              # This file
├── sam/                   # AWS SAM configurations
│   ├── template.yml       # SAM CloudFormation template
│   └── samconfig.toml     # Environment-specific SAM parameters
├── scripts/               # Deployment scripts
│   ├── deploy.sh         # Main deployment script
│   └── run.sh            # Lambda Web Adapter run script
└── environments/          # Environment-specific configurations
    ├── dev.yml           # Development environment config
    ├── staging.yml       # Staging environment config
    └── prod.yml          # Production environment config
```

## 🚀 Quick Deploy

### From Project Root

```bash
# Quick deployment using Makefile
make deploy-dev
make deploy-staging
make deploy-prod

# Or using deployment script directly
./backend/deploy/scripts/deploy.sh dev
./backend/deploy/scripts/deploy.sh staging
./backend/deploy/scripts/deploy.sh prod
```

### From Deploy Directory

```bash
cd backend/deploy

# Using SAM directly
cd sam
sam build --use-container
sam deploy --config-env dev

# Using deployment script
./scripts/deploy.sh dev
```

## ⚙️ Configuration

### SAM Configuration

Edit `sam/samconfig.toml` to update:
- Stack names
- Firebase project IDs
- AWS regions
- Deployment parameters

### Environment Configuration

Edit files in `environments/` directory:
- `dev.yml` - Development settings
- `staging.yml` - Staging settings  
- `prod.yml` - Production settings

These files contain environment-specific values like:
- Resource sizing (memory, timeout)
- Monitoring settings
- CORS origins
- Backup configurations

## 🔧 Customization

### Adding New Environments

1. Create new environment file: `environments/new-env.yml`
2. Add configuration section in `sam/samconfig.toml`
3. Update deployment scripts if needed

### Modifying Resources

Edit `sam/template.yml` to:
- Add new AWS resources
- Modify Lambda function settings
- Update API Gateway configuration
- Change DynamoDB table settings

### Custom Deployment Logic

Edit `scripts/deploy.sh` to:
- Add pre/post deployment hooks
- Modify test execution
- Add custom validation steps

## 📊 Environment Comparison

| Setting | Dev | Staging | Production |
|---------|-----|---------|------------|
| Memory | 512MB | 1024MB | 2048MB |
| Log Retention | 7 days | 14 days | 30 days |
| Point-in-Time Recovery | No | No | Yes |
| X-Ray Tracing | No | Yes | Yes |
| Backup | No | Yes | Yes |

## 🛠️ Advanced Usage

### Manual SAM Commands

```bash
cd sam

# Build only
sam build --use-container

# Local testing
sam local start-api --port 3001

# Deploy with custom parameters
sam deploy --config-env dev --parameter-overrides Environment=dev

# Delete stack
sam delete --config-env dev
```

### Debugging Deployments

```bash
# View CloudFormation events
aws cloudformation describe-stack-events --stack-name blog-api-backend-dev

# Check Lambda logs
aws logs tail /aws/lambda/blog-api-backend-dev-api --follow

# Test deployed API
curl https://your-api-url/api/health
```

## 🔒 Security

- No credentials stored in files
- Environment-specific IAM roles
- CORS configured per environment
- Secrets managed via GitHub environments

## 📋 Troubleshooting

### Common Issues

**Build Failures:**
- Ensure Docker is running for `--use-container` builds
- Check that `run.sh` script is executable
- Verify Python dependencies are correct

**Deployment Failures:**
- Check AWS credentials and permissions
- Verify stack names are unique
- Ensure all required parameters are set

**Runtime Errors:**
- Check Lambda logs for application errors
- Verify environment variables are set correctly
- Test endpoints manually after deployment