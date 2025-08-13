"""Cohorts routes for cohort definition and generation."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..tools.cohorts import (
    add_inclusion_rule,
    define_primary_criteria,
    estimate_cohort_size,
    validate_cohort_definition,
)
from ..tools.persistence import (
    clone_cohort,
    compare_cohorts,
    list_cohorts,
    load_existing_cohort,
    save_cohort_definition,
)

router = APIRouter(prefix="/cohorts", tags=["cohorts"])


# Request models
class PrimaryCriteriaRequest(BaseModel):
    concept_set_id: int
    domain: str
    occurrence_type: str = "First"
    observation_window_prior: int = 0
    observation_window_post: int = 0


class InclusionRuleRequest(BaseModel):
    name: str
    criteria_type: str
    concept_set_id: int
    start_window_start: int | None = None
    start_window_end: int | None = None
    end_window_start: int | None = None
    end_window_end: int | None = None
    occurrence_count: int = 1


class CohortValidationRequest(BaseModel):
    cohort_definition: dict[str, Any]


class CohortSizeEstimateRequest(BaseModel):
    cohort_definition: dict[str, Any]
    source_key: str | None = None


class SaveCohortRequest(BaseModel):
    name: str
    cohort_definition: dict[str, Any]
    description: str | None = None


class LoadCohortRequest(BaseModel):
    cohort_id: int | None = None
    cohort_name: str | None = None


class CompareCohortRequest(BaseModel):
    cohort_a: dict[str, Any]
    cohort_b: dict[str, Any]
    cohort_a_name: str = "Cohort A"
    cohort_b_name: str = "Cohort B"


class CloneCohortRequest(BaseModel):
    source_cohort_id: int
    new_name: str
    modifications: dict[str, Any] | None = None
    new_description: str | None = None


class ListCohortsRequest(BaseModel):
    limit: int = 20
    search_term: str | None = None


# Cohort Building Routes
@router.post("/primary-criteria", summary="Define primary criteria", description="Define primary criteria for cohort index events")
async def define_primary_criteria_endpoint(request: PrimaryCriteriaRequest):
    """Define primary criteria for cohort index events."""
    try:
        result = await define_primary_criteria(
            concept_set_id=request.concept_set_id,
            domain=request.domain,
            occurrence_type=request.occurrence_type,
            observation_window_prior=request.observation_window_prior,
            observation_window_post=request.observation_window_post,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/inclusion-rules", summary="Add inclusion rule", description="Add an inclusion rule to filter cohort subjects")
async def add_inclusion_rule_endpoint(request: InclusionRuleRequest):
    """Add an inclusion rule to filter cohort subjects."""
    try:
        result = await add_inclusion_rule(
            name=request.name,
            criteria_type=request.criteria_type,
            concept_set_id=request.concept_set_id,
            start_window_start=request.start_window_start,
            start_window_end=request.start_window_end,
            end_window_start=request.end_window_start,
            end_window_end=request.end_window_end,
            occurrence_count=request.occurrence_count,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/validate", summary="Validate cohort definition", description="Validate cohort definition syntax and structure")
async def validate_cohort_definition_endpoint(request: CohortValidationRequest):
    """Validate cohort definition syntax and structure."""
    try:
        result = await validate_cohort_definition(request.cohort_definition)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/estimate-size", summary="Estimate cohort size", description="Estimate the size of a cohort without generating it")
async def estimate_cohort_size_endpoint(request: CohortSizeEstimateRequest):
    """Estimate the size of a cohort without generating it."""
    try:
        result = await estimate_cohort_size(cohort_definition=request.cohort_definition, source_key=request.source_key)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Cohort Management Routes (using persistence tools)
@router.post("", summary="Save cohort definition", description="Save a cohort definition")
async def save_cohort_definition_endpoint(request: SaveCohortRequest):
    """Save a cohort definition."""
    try:
        result = await save_cohort_definition(
            name=request.name, cohort_definition=request.cohort_definition, description=request.description
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/list", summary="List cohorts (POST)", description="List available cohort definitions via POST")
async def list_cohorts_post_endpoint(request: ListCohortsRequest):
    """List available cohort definitions via POST."""
    try:
        result = await list_cohorts(limit=request.limit, search_term=request.search_term)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/save", summary="Save cohort definition (POST)", description="Save a cohort definition via POST")
async def save_cohort_post_endpoint(request: SaveCohortRequest):
    """Save a cohort definition via POST."""
    try:
        result = await save_cohort_definition(
            name=request.name, cohort_definition=request.cohort_definition, description=request.description
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", summary="List cohorts", description="List available cohort definitions")
async def list_cohorts_endpoint(
    limit: int = Query(20, description="Maximum number of cohorts to return"),
    search_term: str = Query(None, description="Filter by cohort name"),
):
    """List available cohort definitions."""
    try:
        result = await list_cohorts(limit=limit, search_term=search_term)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/load", summary="Load existing cohort", description="Load an existing cohort definition")
async def load_existing_cohort_endpoint(request: LoadCohortRequest):
    """Load an existing cohort definition."""
    try:
        result = await load_existing_cohort(cohort_id=request.cohort_id, cohort_name=request.cohort_name)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/compare", summary="Compare cohorts", description="Compare two cohort definitions")
async def compare_cohorts_endpoint(request: CompareCohortRequest):
    """Compare two cohort definitions."""
    try:
        result = await compare_cohorts(
            cohort_a=request.cohort_a, cohort_b=request.cohort_b, cohort_a_name=request.cohort_a_name, cohort_b_name=request.cohort_b_name
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/clone", summary="Clone cohort", description="Create a copy of an existing cohort with optional modifications")
async def clone_cohort_endpoint(request: CloneCohortRequest):
    """Create a copy of an existing cohort with optional modifications."""
    try:
        result = await clone_cohort(
            source_cohort_id=request.source_cohort_id,
            new_name=request.new_name,
            modifications=request.modifications,
            new_description=request.new_description,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
