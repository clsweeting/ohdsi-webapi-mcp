"""Vocabulary routes for concept search and vocabulary management."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..tools.vocabulary import (
    browse_concept_hierarchy,
    get_concept_details,
    list_domains,
    list_vocabularies,
    search_concepts,
)

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


# Request models
class ConceptSearchRequest(BaseModel):
    query: str = Field(..., description="Search term for concepts")
    domain: str | None = Field(None, description="Domain filter (e.g., 'Condition', 'Drug')")
    vocabulary: str | None = Field(None, description="Vocabulary filter (e.g., 'SNOMED', 'RxNorm')")
    concept_class: str | None = Field(None, description="Concept class filter")
    standard_only: bool = Field(True, description="Return only standard concepts")
    include_invalid: bool = Field(False, description="Include invalid/deprecated concepts")
    page_size: int = Field(20, description="Maximum number of results")


class ConceptDetailsRequest(BaseModel):
    concept_id: int = Field(..., description="OMOP concept ID")


class ConceptHierarchyRequest(BaseModel):
    concept_id: int = Field(..., description="Starting concept ID")
    direction: str = Field("descendants", description="Direction to browse", pattern="^(descendants|ancestors|both)$")
    max_levels: int = Field(2, description="Maximum hierarchy levels")
    page_size: int = Field(20, description="Maximum concepts per level")


# Response models
class ConceptSearchResponse(BaseModel):
    status: str
    data: list


# Route handlers
@router.post("/search")
async def search_concepts_endpoint(request: ConceptSearchRequest) -> ConceptSearchResponse:
    """Search for medical concepts in OMOP vocabularies."""
    try:
        # Convert page_size back to limit for the tool function
        request_dict = request.model_dump()
        request_dict["limit"] = request_dict.pop("page_size")
        result = await search_concepts(**request_dict)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/details", summary="Get concept details", description="Get detailed information about a specific concept")
async def get_concept_details_endpoint(request: ConceptDetailsRequest):
    """Get detailed information about a specific concept."""
    try:
        result = await get_concept_details(request.concept_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/hierarchy", summary="Browse concept hierarchy", description="Browse concept hierarchy (ancestors/descendants)")
async def browse_concept_hierarchy_endpoint(request: ConceptHierarchyRequest):
    """Browse concept hierarchy (ancestors/descendants)."""
    try:
        # Convert page_size back to limit for the tool function
        request_dict = request.model_dump()
        request_dict["limit"] = request_dict.pop("page_size")
        result = await browse_concept_hierarchy(**request_dict)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/domains", summary="List domains", description="List all available domains in the OMOP CDM")
async def list_domains_endpoint():
    """List all available domains in the OMOP CDM."""
    try:
        result = await list_domains()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/vocabularies", summary="List vocabularies", description="List all available vocabularies in the OMOP CDM")
async def list_vocabularies_endpoint():
    """List all available vocabularies in the OMOP CDM."""
    try:
        result = await list_vocabularies()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
