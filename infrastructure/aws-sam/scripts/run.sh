#!/bin/bash

# Lambda Web Adapter run script for FastAPI Blog API
# This script is executed by Lambda Web Adapter to start the FastAPI application

set -e

# Navigate to the application source code
cd /var/task/src/app

# Set default port if not provided
export PORT=${PORT:-8000}

# Start the FastAPI application with uvicorn
exec uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info --access-log