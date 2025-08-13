"""Concept sets routes for concept set management."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..tools.concept_sets import (
    create_concept_set,
    create_concept_set_from_search,
    get_concept_set_details,
    list_concept_sets,
)

router = APIRouter(prefix="/concept-sets", tags=["concept-sets"])


# Request models
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


# Route handlers
@router.post("/create", summary="Create concept set", description="Create a concept set from a list of concept IDs")
async def create_concept_set_endpoint(request: ConceptSetRequest):
    """Create a concept set from a list of concept IDs."""
    try:
        result = await create_concept_set(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/create-from-search",
    summary="Create concept set from search",
    description="Create a concept set by searching for concepts",
)
async def create_concept_set_from_search_endpoint(request: ConceptSetFromSearchRequest):
    """Create a concept set by searching for concepts."""
    try:
        result = await create_concept_set_from_search(**request.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", summary="List concept sets", description="List all available concept sets")
async def list_concept_sets_endpoint():
    """List all available concept sets."""
    try:
        result = await list_concept_sets()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{concept_set_id}", summary="Get concept set details", description="Get detailed information about a concept set")
async def get_concept_set_details_endpoint(concept_set_id: int):
    """Get detailed information about a concept set."""
    try:
        result = await get_concept_set_details(concept_set_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
