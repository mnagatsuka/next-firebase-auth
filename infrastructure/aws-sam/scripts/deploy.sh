#!/bin/bash

# Deployment script for Blog API Backend (from backend/deploy/ directory)
# Usage: ./backend/deploy/scripts/deploy.sh [environment]
# Environment: development (default), staging, production

set -e

# Configuration
ENV=${1:-development}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$(cd "$DEPLOY_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Validation
validate_environment() {
    case $ENV in
        development|staging|production)
            log_info "Deploying to environment: $ENV"
            ;;
        *)
            log_error "Invalid environment: $ENV. Use development, staging, or production"
            exit 1
            ;;
    esac
}

# Pre-deployment checks
pre_deploy_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if required tools are installed
    command -v aws >/development/null 2>&1 || { log_error "AWS CLI is required but not installed."; exit 1; }
    command -v sam >/development/null 2>&1 || { log_error "AWS SAM CLI is required but not installed."; exit 1; }
    command -v uv >/development/null 2>&1 || { log_error "uv is required but not installed."; exit 1; }
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/development/null 2>&1; then
        log_error "AWS credentials not configured or invalid"
        exit 1
    fi
    
    log_success "Pre-deployment checks passed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    cd "$BACKEND_DIR"
    
    # Run the test suite
    if uv run pytest tests/ -v --tb=short; then
        log_success "All tests passed"
    else
        log_error "Tests failed. Aborting deployment."
        exit 1
    fi
}

# Build and deploy
deploy() {
    log_info "Building and deploying to $ENV environment..."
    
    cd "$DEPLOY_DIR/sam"
    
    # Make run script executable
    chmod +x ../scripts/run.sh
    
    # Build with SAM
    log_info "Building SAM application..."
    if sam build --use-container; then
        log_success "SAM build completed"
    else
        log_error "SAM build failed"
        exit 1
    fi
    
    # Deploy with SAM
    log_info "Deploying with SAM..."
    if sam deploy --config-env "$ENV" --no-confirm-changeset; then
        log_success "SAM deployment completed"
    else
        log_error "SAM deployment failed"
        exit 1
    fi
}

# Get deployment outputs
get_outputs() {
    log_info "Retrieving deployment outputs..."
    
    STACK_NAME="blog-api-backend-$ENV"
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text 2>/development/null || echo "")
    
    # Get Health Check URL
    HEALTH_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`HealthCheckUrl`].OutputValue' \
        --output text 2>/development/null || echo "")
    
    # Get Function Name
    FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' \
        --output text 2>/development/null || echo "")
    
    if [ -z "$API_URL" ]; then
        log_error "Failed to retrieve API URL"
        exit 1
    fi
    
    log_success "Deployment outputs retrieved"
}

# Health check
health_check() {
    log_info "Running health check..."
    
    if [ -z "$HEALTH_URL" ]; then
        log_warning "Health check URL not available, skipping health check"
        return 0
    fi
    
    # Wait for Lambda to be ready
    sleep 30
    
    # Try health check up to 5 times
    for i in {1..5}; do
        log_info "Health check attempt $i/5..."
        
        if curl -f "$HEALTH_URL" --max-time 30 --silent >/development/null 2>&1; then
            log_success "Health check passed"
            return 0
        else
            if [ $i -eq 5 ]; then
                log_error "Health check failed after 5 attempts"
                log_info "You can check the logs with: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
                exit 1
            fi
            log_warning "Health check failed, retrying in 10 seconds..."
            sleep 10
        fi
    done
}

# Print deployment summary
print_summary() {
    echo
    echo "=========================================="
    echo "🚀 DEPLOYMENT COMPLETED SUCCESSFULLY! 🚀"
    echo "=========================================="
    echo
    echo "Environment: $ENV"
    echo "Stack Name: blog-api-backend-$ENV"
    echo
    if [ -n "$API_URL" ]; then
        echo "🌐 API URL: $API_URL"
    fi
    if [ -n "$HEALTH_URL" ]; then
        echo "❤️  Health Check: $HEALTH_URL"
    fi
    if [ -n "$FUNCTION_NAME" ]; then
        echo "⚡ Function: $FUNCTION_NAME"
        echo
        echo "📊 Useful commands:"
        echo "  View logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
        echo "  Test API:  curl $API_URL/api/health"
    fi
    echo
}

# Main execution
main() {
    echo "🚀 Blog API Backend Deployment Script"
    echo "======================================"
    echo "Deploy Directory: $DEPLOY_DIR"
    
    validate_environment
    pre_deploy_checks
    run_tests
    deploy
    get_outputs
    health_check
    print_summary
    
    log_success "Deployment script completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Execute main function
main "$@"