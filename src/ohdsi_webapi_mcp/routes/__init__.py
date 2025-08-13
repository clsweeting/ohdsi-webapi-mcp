"""Routes package for the OHDSI WebAPI MCP server."""

from .cohorts import router as cohorts_router
from .concept_sets import router as concept_sets_router
from .info import router as info_router
from .jobs import router as jobs_router
from .persistence import router as persistence_router
from .sources import router as sources_router
from .vocabulary import router as vocabulary_router

__all__ = [
    "vocabulary_router",
    "concept_sets_router",
    "info_router",
    "sources_router",
    "jobs_router",
    "cohorts_router",
    "persistence_router",
]
