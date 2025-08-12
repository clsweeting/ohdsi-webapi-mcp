"""HTTP server implementation for OHDSI WebAPI MCP server.

This module provides a FastAPI HTTP server that exposes OHDSI WebAPI functionality
as both REST endpoints and MCP tools via fastapi-mcp integration.
"""

import logging
import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel, Field

from .tools.cohorts import add_inclusion_rule, create_concept_set, define_primary_criteria, estimate_cohort_size, validate_cohort_definition
from .tools.concepts import (
    browse_concept_hierarchy,
    create_concept_set_from_search,
    get_concept_details,
    list_domains,
    list_vocabularies,
    search_concepts,
)
from .tools.persistence import clone_cohort, compare_cohorts, list_cohorts, load_existing_cohort, save_cohort_definition

"""HTTP server implementation for OHDSI WebAPI MCP server.

This module provides a FastAPI HTTP server that exposes OHDSI WebAPI functionality
as both REST endpoints and MCP tools via fastapi-mcp integration.
"""


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


# Pydantic models for request/response
class ConceptSearchRequest(BaseModel):
    query: str = Field(..., description="Search term for concepts")
    domain: str | None = Field(None, description="Domain filter (e.g., 'Condition', 'Drug')")
    vocabulary: str | None = Field(None, description="Vocabulary filter (e.g., 'SNOMED', 'RxNorm')")
    concept_class: str | None = Field(None, description="Concept class filter")
    standard_only: bool = Field(True, description="Return only standard concepts")
    include_invalid: bool = Field(False, description="Include invalid/deprecated concepts")
    limit: int = Field(20, description="Maximum number of results")


class ConceptDetailsRequest(BaseModel):
    concept_id: int = Field(..., description="OMOP concept ID")


class ConceptHierarchyRequest(BaseModel):
    concept_id: int = Field(..., description="Starting concept ID")
    direction: str = Field("descendants", description="Direction to browse", pattern="^(descendants|ancestors|both)$")
    max_levels: int = Field(2, description="Maximum hierarchy levels")
    limit: int = Field(20, description="Maximum concepts per level")


class ConceptSetRequest(BaseModel):
    name: str = Field(..., description="Name for the concept set")
    concept_ids: list[int] = Field(..., description="List of concept IDs")
    include_descendants: bool = Field(True, description="Include descendant concepts")
    include_mapped: bool = Field(False, description="Include mapped concepts")


class ConceptSetFromSearchRequest(BaseModel):
    name: str = Field(..., description="Name for the concept set")
    search_queries: list[str] = Field(..., description="Search terms to find concepts")
    domain: str | None = Field(None, description="Domain filter")
    vocabulary: str | None = Field(None, description="Vocabulary filter")
    include_descendants: bool = Field(True, description="Include descendant concepts")
    include_mapped: bool = Field(False, description="Include mapped concepts")
    max_concepts_per_query: int = Field(10, description="Max concepts per search")


class PrimaryCriteriaRequest(BaseModel):
    concept_set_id: int = Field(..., description="ID of concept set to use")
    domain: str = Field(
        ...,
        description="Domain type",
        pattern="^(ConditionOccurrence|DrugExposure|ProcedureOccurrence|Measurement|Observation|DeviceExposure)$",
    )
    occurrence_type: str = Field("First", description="Occurrence selection", pattern="^(First|All)$")
    observation_window_prior: int = Field(0, description="Prior observation days")
    observation_window_post: int = Field(0, description="Post observation days")


class InclusionRuleRequest(BaseModel):
    name: str = Field(..., description="Name of the inclusion rule")
    criteria_type: str = Field(
        ...,
        description="Type of criteria",
        pattern="^(ConditionOccurrence|DrugExposure|ProcedureOccurrence|Measurement|Observation|DeviceExposure)$",
    )
    concept_set_id: int = Field(..., description="ID of concept set to use")
    start_window_start: int | None = Field(None, description="Start window start days")
    start_window_end: int | None = Field(None, description="Start window end days")
    end_window_start: int | None = Field(None, description="End window start days")
    end_window_end: int | None = Field(None, description="End window end days")
    occurrence_count: int = Field(1, description="Required occurrences")


class CohortValidationRequest(BaseModel):
    cohort_definition: dict[str, Any] = Field(..., description="Cohort definition JSON")


class CohortSizeRequest(BaseModel):
    cohort_definition: dict[str, Any] = Field(..., description="Cohort definition JSON")
    source_key: str | None = Field(None, description="CDM source key")


class SaveCohortRequest(BaseModel):
    name: str = Field(..., description="Name for the cohort")
    cohort_definition: dict[str, Any] = Field(..., description="Cohort definition JSON")
    description: str | None = Field(None, description="Description of the cohort")


class LoadCohortRequest(BaseModel):
    cohort_id: int | None = Field(None, description="Cohort ID to load")
    cohort_name: str | None = Field(None, description="Cohort name to search for")


class ListCohortsRequest(BaseModel):
    limit: int = Field(20, description="Maximum results")
    search_term: str | None = Field(None, description="Filter by name")


class CompareCohortRequest(BaseModel):
    cohort_a: dict[str, Any] = Field(..., description="First cohort definition")
    cohort_b: dict[str, Any] = Field(..., description="Second cohort definition")
    cohort_a_name: str = Field("Cohort A", description="Name for first cohort")
    cohort_b_name: str = Field("Cohort B", description="Name for second cohort")


class CloneCohortRequest(BaseModel):
    source_cohort_id: int = Field(..., description="ID of cohort to clone")
    new_name: str = Field(..., description="Name for cloned cohort")
    modifications: dict[str, Any] | None = Field(None, description="Modifications to apply")
    new_description: str | None = Field(None, description="Description for cloned cohort")


# Create FastAPI app
app = FastAPI(
    title="OHDSI WebAPI MCP Server",
    description="HTTP server providing OHDSI WebAPI functionality as both REST endpoints and MCP tools",
    version="0.1.0",
)

# Add MCP integration
mcp = FastApiMCP(app)

# Mount the MCP server at /mcp endpoint
mcp.mount()


# Concept Discovery Endpoints
@app.post("/concepts/search", summary="Search for medical concepts", description="Search for medical concepts in OMOP vocabularies")
async def search_concepts_endpoint(request: ConceptSearchRequest, config=Depends(get_webapi_config)):
    """Search for medical concepts in OMOP vocabularies."""
    try:
        result = await search_concepts(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/concepts/details", summary="Get concept details", description="Get detailed information about a specific concept")
async def get_concept_details_endpoint(request: ConceptDetailsRequest, config=Depends(get_webapi_config)):
    """Get detailed information about a specific concept."""
    try:
        result = await get_concept_details(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/concepts/hierarchy", summary="Browse concept hierarchy", description="Browse concept hierarchy (ancestors/descendants)")
async def browse_concept_hierarchy_endpoint(request: ConceptHierarchyRequest, config=Depends(get_webapi_config)):
    """Browse concept hierarchy (ancestors/descendants)."""
    try:
        result = await browse_concept_hierarchy(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/concepts/domains", summary="List domains", description="List all available domains in the OMOP CDM")
async def list_domains_endpoint(config=Depends(get_webapi_config)):
    """List all available domains in the OMOP CDM."""
    try:
        result = await list_domains()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/concepts/vocabularies", summary="List vocabularies", description="List all available vocabularies in the OMOP CDM")
async def list_vocabularies_endpoint(config=Depends(get_webapi_config)):
    """List all available vocabularies in the OMOP CDM."""
    try:
        result = await list_vocabularies()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Concept Set Endpoints
@app.post("/concept-sets/create", summary="Create concept set", description="Create a concept set from a list of concept IDs")
async def create_concept_set_endpoint(request: ConceptSetRequest, config=Depends(get_webapi_config)):
    """Create a concept set from a list of concept IDs."""
    try:
        result = await create_concept_set(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/concept-sets/create-from-search",
    summary="Create concept set from search",
    description="Create a concept set by searching for concepts",
)
async def create_concept_set_from_search_endpoint(request: ConceptSetFromSearchRequest, config=Depends(get_webapi_config)):
    """Create a concept set by searching for concepts."""
    try:
        result = await create_concept_set_from_search(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Cohort Building Endpoints
@app.post("/cohorts/primary-criteria", summary="Define primary criteria", description="Define primary criteria for cohort index events")
async def define_primary_criteria_endpoint(request: PrimaryCriteriaRequest, config=Depends(get_webapi_config)):
    """Define primary criteria for cohort index events."""
    try:
        result = await define_primary_criteria(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/inclusion-rules", summary="Add inclusion rule", description="Add an inclusion rule to filter cohort subjects")
async def add_inclusion_rule_endpoint(request: InclusionRuleRequest, config=Depends(get_webapi_config)):
    """Add an inclusion rule to filter cohort subjects."""
    try:
        result = await add_inclusion_rule(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/validate", summary="Validate cohort definition", description="Validate a cohort definition for correctness")
async def validate_cohort_definition_endpoint(request: CohortValidationRequest, config=Depends(get_webapi_config)):
    """Validate a cohort definition for correctness."""
    try:
        result = await validate_cohort_definition(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/estimate-size", summary="Estimate cohort size", description="Estimate the size of a cohort without generating it")
async def estimate_cohort_size_endpoint(request: CohortSizeRequest, config=Depends(get_webapi_config)):
    """Estimate the size of a cohort without generating it."""
    try:
        result = await estimate_cohort_size(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Persistence & Management Endpoints
@app.post("/cohorts/save", summary="Save cohort definition", description="Save a cohort definition to the WebAPI")
async def save_cohort_definition_endpoint(request: SaveCohortRequest, config=Depends(get_webapi_config)):
    """Save a cohort definition to the WebAPI."""
    try:
        result = await save_cohort_definition(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/load", summary="Load existing cohort", description="Load an existing cohort definition from WebAPI")
async def load_existing_cohort_endpoint(request: LoadCohortRequest, config=Depends(get_webapi_config)):
    """Load an existing cohort definition from WebAPI."""
    try:
        result = await load_existing_cohort(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/list", summary="List cohorts", description="List available cohort definitions")
async def list_cohorts_endpoint(request: ListCohortsRequest, config=Depends(get_webapi_config)):
    """List available cohort definitions."""
    try:
        result = await list_cohorts(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/compare", summary="Compare cohorts", description="Compare two cohort definitions")
async def compare_cohorts_endpoint(request: CompareCohortRequest, config=Depends(get_webapi_config)):
    """Compare two cohort definitions."""
    try:
        result = await compare_cohorts(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cohorts/clone", summary="Clone cohort", description="Clone an existing cohort with optional modifications")
async def clone_cohort_endpoint(request: CloneCohortRequest, config=Depends(get_webapi_config)):
    """Clone an existing cohort with optional modifications."""
    try:
        result = await clone_cohort(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


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
