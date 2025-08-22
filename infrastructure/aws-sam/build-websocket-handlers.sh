#!/bin/bash

# Build WebSocket handlers for AWS SAM deployment
# This script installs dependencies for TypeScript handlers with AWS SDK v3

set -e

echo "Building WebSocket handlers for AWS SAM deployment..."

# Navigate to websocket-handlers directory
cd websocket-handlers/

# Install dependencies
if [ ! -f "package.json" ]; then
  echo "❌ package.json not found in websocket-handlers directory"
  exit 1
fi

echo "Installing dependencies..."
pnpm install --production

# Note: SAM will handle TypeScript compilation with esbuild automatically
# based on the BuildMethod: esbuild configuration in template.yml

cd ..

echo "✅ WebSocket handlers built successfully!"
echo "📁 Dependencies installed in websocket-handlers/"
echo "📝 SAM will compile TypeScript files automatically during build"