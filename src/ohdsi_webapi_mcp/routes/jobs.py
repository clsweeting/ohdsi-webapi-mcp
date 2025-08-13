"""Jobs routes for background job management."""

from fastapi import APIRouter, HTTPException, Query

from ..tools.jobs import (
    cancel_job,
    get_job_status,
    list_recent_jobs,
    monitor_job_progress,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


# Route handlers
@router.get("", summary="List recent jobs", description="List recent background jobs")
async def list_recent_jobs_endpoint(limit: int = Query(20, description="Maximum number of jobs to return")):
    """List recent background jobs."""
    try:
        result = await list_recent_jobs(limit=limit)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{execution_id}", summary="Get job status", description="Get detailed status of a specific job")
async def get_job_status_endpoint(execution_id: str):
    """Get detailed status of a specific job."""
    try:
        result = await get_job_status(execution_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{execution_id}", summary="Cancel job", description="Cancel a running job")
async def cancel_job_endpoint(execution_id: str):
    """Cancel a running job."""
    try:
        result = await cancel_job(execution_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{execution_id}/monitor", summary="Monitor job progress", description="Monitor job progress with status updates")
async def monitor_job_progress_endpoint(execution_id: str):
    """Monitor job progress with status updates."""
    try:
        result = await monitor_job_progress(execution_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
