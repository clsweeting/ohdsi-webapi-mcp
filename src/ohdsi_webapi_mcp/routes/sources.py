"""Sources routes for CDM source management."""

from fastapi import APIRouter, HTTPException

from ..tools.sources import (
    get_default_source,
    get_source_details,
    list_data_sources,
)

router = APIRouter(prefix="/sources", tags=["sources"])


# Route handlers
@router.get("", summary="List data sources", description="List all CDM data sources")
async def list_data_sources_endpoint():
    """List all CDM data sources."""
    try:
        result = await list_data_sources()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{source_key}", summary="Get source details", description="Get detailed information about a CDM source")
async def get_source_details_endpoint(source_key: str):
    """Get detailed information about a CDM source."""
    try:
        result = await get_source_details(source_key)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/default/info", summary="Get default source", description="Get information about the default data source")
async def get_default_source_endpoint():
    """Get information about the default data source."""
    try:
        result = await get_default_source()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
