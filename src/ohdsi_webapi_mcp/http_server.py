"""HTTP server implementation for OHDSI WebAPI MCP server.

This module provides a FastAPI HTTP server that exposes OHDSI WebAPI functionality
as both REST endpoints and MCP tools via fastapi-mcp integration.
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP

from .routes import (
    cohorts_router,
    concept_sets_router,
    info_router,
    jobs_router,
    persistence_router,
    sources_router,
    vocabulary_router,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_webapi_config():
    """Get WebAPI configuration from environment variables."""
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise HTTPException(status_code=500, detail="WEBAPI_BASE_URL environment variable is required")

    return {
        "webapi_base_url": webapi_base_url,
        "webapi_source_key": os.getenv("WEBAPI_SOURCE_KEY"),
    }


# Create FastAPI app
app = FastAPI(
    title="OHDSI WebAPI MCP Server",
    description="HTTP server providing OHDSI WebAPI functionality as both REST endpoints and MCP tools",
    version="0.1.0",
)

# Add MCP integration
mcp = FastApiMCP(app)

# Mount the MCP server at the default endpoint (usually /mcp)
mcp.mount()

# Include routers from the routes package
app.include_router(vocabulary_router)
app.include_router(concept_sets_router)
app.include_router(info_router)
app.include_router(jobs_router)
app.include_router(sources_router)
app.include_router(cohorts_router)
app.include_router(persistence_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ohdsi-webapi-mcp"}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


def main():
    """Main entry point for the HTTP server."""
    import uvicorn

    port = int(os.getenv("MCP_PORT", "8000"))
    host = os.getenv("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting OHDSI WebAPI MCP HTTP server on {host}:{port}")
    logger.info(f"MCP endpoint will be available at http://{host}:{port}/mcp")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
