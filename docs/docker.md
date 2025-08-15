# Docker Usage Guide

This document explains how to use the OHDSI WebAPI MCP Server with Docker.


### Docker Compose

A [docker-compose.yml](../docker-compose.yml) is provided. 

```bash
# Start with docker-compose
docker-compose up -d

# Stop
docker-compose down
```

### Building Local Docker Image
```bash
# Clone and build
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
docker build -t ohdsi-webapi-mcp-local .

# Run HTTP mode
docker run -p 8000:8000 --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ohdsi-webapi-mcp-local http
```


## Quick Start

### 1. Pull and Run (Simplest)
```bash
# Pull the pre-built image and run
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  -e WEBAPI_SOURCE_KEY="EUNOMIA" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest
```

### 2. Build from Source
```bash
# Clone the repository
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp

# Build the image
docker build -t ohdsi-webapi-mcp .

# Run your built image
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://your-atlas.org/WebAPI" \
  -e WEBAPI_SOURCE_KEY="YOUR_SOURCE" \
  ohdsi-webapi-mcp
```

## MCP Client Configuration

### Claude Desktop
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI",
        "-e", "WEBAPI_SOURCE_KEY=EUNOMIA",
        "ghcr.io/clsweeting/ohdsi-webapi-mcp:latest"
      ]
    }
  }
}
```

### Cline (VS Code)
Add this to your VS Code settings:

```json
{
  "cline.mcp.servers": [
    {
      "name": "ohdsi-webapi",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "WEBAPI_BASE_URL=https://your-atlas.org/WebAPI",
        "-e", "WEBAPI_SOURCE_KEY=YOUR_SOURCE",
        "ghcr.io/clsweeting/ohdsi-webapi-mcp:latest"
      ]
    }
  ]
}
```

## Environment Variables

Configure these environment variables for your OHDSI setup:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WEBAPI_BASE_URL` | Yes | Your OHDSI WebAPI base URL | `https://atlas-demo.ohdsi.org/WebAPI` |
| `WEBAPI_SOURCE_KEY` | Yes | Your CDM data source key | `EUNOMIA`, `SYNPUF1K` |
| `LOG_LEVEL` | No | Logging level | `INFO` (default), `DEBUG`, `WARNING`, `ERROR` |

## Development with Docker

### Using Docker Compose
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your settings

# Run with Docker Compose
docker-compose up ohdsi-webapi-mcp-prod
```

### Development Mode
```bash
# Run with local code mounted (for development)
docker-compose --profile dev up ohdsi-webapi-mcp
```

### Helper Script
Use the included `docker.sh` script for common tasks:

```bash
# Build image
./docker.sh build

# Run server
./docker.sh run

# Test image
./docker.sh test

# Clean up
./docker.sh clean

# Run with Docker Compose
./docker.sh compose
```

### Makefile Commands
```bash
# Docker commands via Make
make docker-build
make docker-run
make docker-test
make docker-clean
```

## Advantages of Docker

✅ **No Python installation required** - Works on any system with Docker  
✅ **Isolated dependencies** - No conflicts with your system Python  
✅ **Consistent environment** - Same runtime everywhere  
✅ **Easy deployment** - Single container to run  
✅ **Version pinning** - Exact reproducible builds  
✅ **Cross-platform** - Works on macOS, Linux, Windows  

## Multi-Architecture Support

The Docker images are built for multiple architectures:
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (Apple Silicon, ARM64)

Docker will automatically pull the correct image for your platform.

## Troubleshooting

### Docker Daemon Not Running
```bash
# Check if Docker is running
docker info

# Start Docker Desktop (macOS/Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

### Permission Denied
```bash
# Add your user to docker group (Linux)
sudo usermod -aG docker $USER
# Then log out and back in
```

### Image Not Found
```bash
# Pull the latest image manually
docker pull ghcr.io/clsweeting/ohdsi-webapi-mcp:latest

# Or build from source
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
docker build -t ohdsi-webapi-mcp .
```

### Environment Variables Not Working
Make sure to use the `-e` flag for each environment variable:
```bash
docker run -i --rm \
  -e WEBAPI_BASE_URL="your-url" \
  -e WEBAPI_SOURCE_KEY="your-key" \
  ohdsi-webapi-mcp
```

## Security Considerations

- The container runs as a non-root user (`mcpuser`)
- No sensitive data is stored in the image
- Environment variables are passed at runtime
- Network access is only for WebAPI communication

## Image Information

- **Base Image**: `python:3.11-slim`
- **Image Size**: ~150MB (optimized)
- **User**: `mcpuser` (non-root)
- **Exposed Ports**: None (stdin/stdout communication)
- **Health Check**: Built-in `--help` test



### Docker Debugging
```bash
# Check container logs
docker run -p 8000:8000 \
  -e WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
  -e LOG_LEVEL=DEBUG \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest http

# Or with docker-compose
docker-compose logs -f ohdsi-mcp
```

