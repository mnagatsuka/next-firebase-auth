# GitHub Deployment Setup Guide

This guide shows how to configure GitHub environments and secrets for automated deployments.

## 1. Create GitHub Environments

Go to your repository **Settings** → **Environments** and create:

### Development Environment (`dev`)
- **Environment name**: `dev`
- **Deployment branches**: Any branch
- **Required reviewers**: None (optional)

**Environment Secrets:**
```
AWS_ACCESS_KEY_ID=your-dev-aws-access-key
AWS_SECRET_ACCESS_KEY=your-dev-aws-secret-key
```

### Staging Environment (`staging`) 
- **Environment name**: `staging`
- **Deployment branches**: `main` branch only
- **Required reviewers**: Optional

**Environment Secrets:**
```
AWS_ACCESS_KEY_ID=your-staging-aws-access-key
AWS_SECRET_ACCESS_KEY=your-staging-aws-secret-key
```

### Production Environment (`prod`)
- **Environment name**: `prod`
- **Deployment branches**: `production` branch only
- **Required reviewers**: Required (recommended)

**Environment Secrets:**
```
AWS_ACCESS_KEY_ID=your-prod-aws-access-key
AWS_SECRET_ACCESS_KEY=your-prod-aws-secret-key
```

## 2. AWS IAM Setup

### Create Deployment Users

Create separate IAM users for each environment:

```bash
# Development user
aws iam create-user --user-name blog-api-deploy-dev

# Staging user  
aws iam create-user --user-name blog-api-deploy-staging

# Production user
aws iam create-user --user-name blog-api-deploy-prod
```

### Attach Policies

Create and attach a deployment policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "s3:*",
                "lambda:*",
                "apigateway:*",
                "dynamodb:*",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PassRole",
                "logs:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Generate Access Keys

```bash
# For each environment user
aws iam create-access-key --user-name blog-api-deploy-dev
aws iam create-access-key --user-name blog-api-deploy-staging
aws iam create-access-key --user-name blog-api-deploy-prod
```

## 3. Update Firebase Project IDs

Edit `backend/samconfig.toml` with your actual Firebase project IDs:

```toml
# Development
[dev.deploy.parameters]
parameter_overrides = [
    "Environment=dev",
    "FirebaseProjectId=your-actual-dev-firebase-project"  # Update this
]

# Staging
[staging.deploy.parameters] 
parameter_overrides = [
    "Environment=staging",
    "FirebaseProjectId=your-actual-staging-firebase-project"  # Update this
]

# Production
[prod.deploy.parameters]
parameter_overrides = [
    "Environment=prod", 
    "FirebaseProjectId=your-actual-prod-firebase-project"  # Update this
]
```

## 4. Test Deployment

### Manual Test
Go to **Actions** tab → **Deploy Backend API** → **Run workflow**
- Choose environment: `dev`
- Click **Run workflow**

### Automatic Test
Push changes to backend files on `main` branch to trigger staging deployment.

## 5. Security Best Practices

### Environment Protection Rules
- **Development**: No restrictions
- **Staging**: Restrict to `main` branch
- **Production**: Restrict to `production` branch + require reviews

### Secrets Management
- Never commit AWS credentials to repository
- Use different AWS accounts/users per environment
- Rotate access keys regularly
- Use least-privilege IAM policies

### Branch Strategy
```
main branch        → Staging deployment
production branch  → Production deployment  
feature branches   → Manual dev deployments only
```

## 6. Monitoring Setup

Add notification webhooks (optional):

1. Go to **Settings** → **Webhooks**
2. Add webhook URL for deployment notifications
3. Select events: `Deployment`, `Deployment status`

## 7. Troubleshooting

### Common Issues

**"Environment not found"**
- Verify environment names match exactly (`dev`, `staging`, `prod`)
- Check environment is created in repository settings

**"Invalid AWS credentials"**
- Verify access keys are correct in environment secrets
- Check IAM user has required permissions
- Ensure secrets are added to correct environment

**"Stack already exists"** 
- Delete existing stack: `aws cloudformation delete-stack --stack-name blog-api-backend-dev`
- Or use different stack names in `samconfig.toml`

### Verify Setup

```bash
# Check if environments work
curl -f https://your-api-url/api/health

# View deployment logs in GitHub Actions
# Go to Actions tab → Recent workflow run → View logs
```