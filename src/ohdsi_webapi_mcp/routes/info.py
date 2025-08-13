"""Info routes for WebAPI system information."""

from fastapi import APIRouter, HTTPException

from ..tools.info import (
    check_webapi_health,
    get_webapi_info,
    get_webapi_version,
)

router = APIRouter(prefix="/info", tags=["info"])


# Route handlers
@router.get("", summary="Get WebAPI info", description="Get WebAPI version and system information")
async def get_webapi_info_endpoint():
    """Get WebAPI version and system information."""
    try:
        result = await get_webapi_info()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/version", summary="Get WebAPI version", description="Get WebAPI version information")
async def get_webapi_version_endpoint():
    """Get WebAPI version information."""
    try:
        result = await get_webapi_version()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/health", summary="Check WebAPI health", description="Check WebAPI health and connectivity")
async def check_webapi_health_endpoint():
    """Check WebAPI health and connectivity."""
    try:
        result = await check_webapi_health()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
