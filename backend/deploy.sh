#!/bin/bash

echo "Deploying HushMCP Agent API to Vercel..."
echo ""

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "Error: Vercel CLI is not installed"
    echo "Please install it with: npm install -g vercel"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo ""

# Deploy to Vercel
echo "Starting deployment..."
vercel --prod

echo ""
echo "Deployment completed!"
echo "Check the Vercel dashboard for deployment status and URL."
