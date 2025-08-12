#!/bin/bash
# Docker development and testing script

set -e

echo "🐳 OHDSI WebAPI MCP Docker Helper"
echo "=================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    echo "Please start Docker Desktop or the Docker daemon"
    exit 1
fi

IMAGE_NAME="ohdsi-webapi-mcp"
TAG="latest"

case "${1:-help}" in
    "build")
        echo "🔨 Building Docker image..."
        docker build -t "$IMAGE_NAME:$TAG" .
        echo "✅ Image built successfully: $IMAGE_NAME:$TAG"
        ;;
    
    "run")
        echo "🚀 Running MCP server in Docker..."
        docker run -i --rm \
            -e WEBAPI_BASE_URL="${WEBAPI_BASE_URL:-https://atlas-demo.ohdsi.org/WebAPI}" \
            -e WEBAPI_SOURCE_KEY="${WEBAPI_SOURCE_KEY:-EUNOMIA}" \
            "$IMAGE_NAME:$TAG"
        ;;
    
    "test")
        echo "🧪 Testing Docker image..."
        if docker run --rm "$IMAGE_NAME:$TAG" --help > /dev/null 2>&1; then
            echo "✅ Docker image test passed"
        else
            echo "❌ Docker image test failed"
            exit 1
        fi
        ;;
    
    "clean")
        echo "🧹 Cleaning up Docker images..."
        docker rmi "$IMAGE_NAME:$TAG" 2>/dev/null || echo "No image to remove"
        echo "✅ Cleanup complete"
        ;;
    
    "compose")
        echo "🎼 Starting with Docker Compose..."
        docker-compose up ohdsi-webapi-mcp-prod
        ;;
    
    "help"|*)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build     Build the Docker image"
        echo "  run       Run the MCP server in Docker"
        echo "  test      Test the Docker image"
        echo "  clean     Remove the Docker image"
        echo "  compose   Run with Docker Compose"
        echo "  help      Show this help message"
        echo ""
        echo "Environment variables:"
        echo "  WEBAPI_BASE_URL   - OHDSI WebAPI base URL"
        echo "  WEBAPI_SOURCE_KEY - CDM source key"
        ;;
esac
