"""
FastAPI HTTP server for OHDSI WebAPI MCP tools.

This module creates an HTTP API server that exposes the MCP tools as REST endpoints,
making them accessible via HTTP requests in addition to the MCP protocol.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from .routes.cohorts import router as cohorts_router
from .routes.concept_sets import router as concept_sets_router
from .routes.info import router as info_router
from .routes.jobs import router as jobs_router
from .routes.persistence import router as persistence_router
from .routes.sources import router as sources_router
from .routes.vocabulary import router as vocabulary_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Create FastAPI app
    app = FastAPI(
        title="OHDSI WebAPI MCP Server",
        description="HTTP API for OHDSI WebAPI Model Context Protocol tools",
        version="0.1.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize MCP integration
    _mcp = FastApiMCP(app)  # Keep reference to prevent garbage collection

    # Include routers
    app.include_router(vocabulary_router)
    app.include_router(concept_sets_router)
    app.include_router(cohorts_router)
    app.include_router(info_router)
    app.include_router(jobs_router)
    app.include_router(sources_router)
    app.include_router(persistence_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "ohdsi-webapi-mcp"}

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
