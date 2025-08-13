"""Tools for WebAPI job management and monitoring."""

import asyncio
import os

import mcp.types as types
from ohdsi_webapi import WebApiClient


async def get_job_status(execution_id: str) -> list[types.TextContent]:
    """Get the status of a WebAPI job execution.

    Parameters
    ----------
    execution_id : str
        The execution ID to check status for.

    Returns
    -------
    List[types.TextContent]
        Job status information formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_get_job_status():
        client = WebApiClient(webapi_base_url)
        try:
            # Get job status
            status = client.jobs.status(execution_id)

            if not status:
                return [types.TextContent(type="text", text=f"No job found with execution ID: {execution_id}")]

            result = f"""Job Status for Execution ID: {execution_id}

Status: {getattr(status, 'status', 'Unknown')}"""

            # Add job details if available
            if hasattr(status, "job_name"):
                result += f"\nJob Name: {status.job_name}"

            if hasattr(status, "job_type"):
                result += f"\nJob Type: {status.job_type}"

            if hasattr(status, "start_time"):
                result += f"\nStart Time: {status.start_time}"

            if hasattr(status, "end_time") and status.end_time:
                result += f"\nEnd Time: {status.end_time}"

            if hasattr(status, "duration") and status.duration:
                result += f"\nDuration: {status.duration}"

            if hasattr(status, "progress") and status.progress is not None:
                result += f"\nProgress: {status.progress}%"

            if hasattr(status, "message") and status.message:
                result += f"\nMessage: {status.message}"

            if hasattr(status, "failure_message") and status.failure_message:
                result += f"\n⚠️  Failure Message: {status.failure_message}"

            # Add any other relevant fields
            if hasattr(status, "__dict__"):
                other_fields = []
                shown_fields = {
                    "status",
                    "job_name",
                    "job_type",
                    "start_time",
                    "end_time",
                    "duration",
                    "progress",
                    "message",
                    "failure_message",
                }

                for key, value in status.__dict__.items():
                    if key not in shown_fields and not key.startswith("_") and value is not None:
                        other_fields.append(f"{key}: {value}")

                if other_fields:
                    result += "\n\nAdditional Information:"
                    for field in other_fields:
                        result += f"\n  - {field}"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving job status: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_job_status)


async def list_recent_jobs(limit: int = 20) -> list[types.TextContent]:
    """List recent job executions.

    Parameters
    ----------
    limit : int, optional
        Maximum number of jobs to return, by default 20.

    Returns
    -------
    List[types.TextContent]
        List of recent jobs formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_list_jobs():
        client = WebApiClient(webapi_base_url)
        try:
            # Try to get recent jobs - this method may not exist in all WebAPI versions
            if hasattr(client.jobs, "list"):
                jobs = client.jobs.list(limit=limit)
            else:
                return [types.TextContent(type="text", text="Job listing not available in this WebAPI version")]

            if not jobs:
                return [types.TextContent(type="text", text="No recent jobs found")]

            result = f"Recent Job Executions ({len(jobs)} shown):\n\n"

            for job in jobs:
                # Format job info
                job_info = f"• Execution ID: {getattr(job, 'execution_id', 'Unknown')}"

                if hasattr(job, "job_name"):
                    job_info += f"\n  Name: {job.job_name}"

                if hasattr(job, "status"):
                    status_emoji = {"COMPLETED": "✅", "RUNNING": "🔄", "FAILED": "❌", "PENDING": "⏳", "CANCELED": "⏹️"}.get(
                        job.status.upper(), "❓"
                    )
                    job_info += f"\n  Status: {status_emoji} {job.status}"

                if hasattr(job, "start_time"):
                    job_info += f"\n  Started: {job.start_time}"

                if hasattr(job, "duration") and job.duration:
                    job_info += f"\n  Duration: {job.duration}"

                result += job_info + "\n\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving job list: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_list_jobs)


async def cancel_job(execution_id: str) -> list[types.TextContent]:
    """Cancel a running job execution.

    Parameters
    ----------
    execution_id : str
        The execution ID of the job to cancel.

    Returns
    -------
    List[types.TextContent]
        Job cancellation result formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_cancel_job():
        client = WebApiClient(webapi_base_url)
        try:
            # Check if cancel method exists
            if not hasattr(client.jobs, "cancel"):
                return [types.TextContent(type="text", text="Job cancellation not available in this WebAPI version")]

            # First check current status
            current_status = client.jobs.status(execution_id)
            if not current_status:
                return [types.TextContent(type="text", text=f"No job found with execution ID: {execution_id}")]

            if hasattr(current_status, "status") and current_status.status.upper() in ["COMPLETED", "FAILED", "CANCELED"]:
                return [
                    types.TextContent(
                        type="text", text=f"Job {execution_id} is already {current_status.status.lower()} and cannot be canceled"
                    )
                ]

            # Attempt to cancel
            result_obj = client.jobs.cancel(execution_id)

            # Check the result
            result = f"""Job Cancellation Request for {execution_id}:

Status: Cancellation requested"""

            if result_obj:
                if hasattr(result_obj, "success") and result_obj.success:
                    result += "\nResult: ✅ Successfully canceled"
                elif hasattr(result_obj, "message"):
                    result += f"\nMessage: {result_obj.message}"
                else:
                    result += "\nResult: Cancellation request submitted"
            else:
                result += "\nResult: Cancellation request submitted"

            result += f"\n\nTo check the current status, use: get_job_status('{execution_id}')"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error canceling job: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_cancel_job)


async def monitor_job_progress(execution_id: str, check_interval: int = 30) -> list[types.TextContent]:
    """Monitor job progress with periodic status checks.

    Parameters
    ----------
    execution_id : str
        The execution ID to monitor.
    check_interval : int, optional
        Seconds between status checks, by default 30.

    Returns
    -------
    List[types.TextContent]
        Job monitoring information formatted for MCP client.
    """
    # Note: This is a simplified version for MCP - in a real implementation
    # you might want to use background tasks or streaming responses

    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_monitor_job():
        client = WebApiClient(webapi_base_url)
        try:
            # Get current status
            status = client.jobs.status(execution_id)

            if not status:
                return [types.TextContent(type="text", text=f"No job found with execution ID: {execution_id}")]

            result = f"""Job Monitor for Execution ID: {execution_id}

Current Status: {getattr(status, 'status', 'Unknown')}"""

            if hasattr(status, "progress") and status.progress is not None:
                result += f"\nProgress: {status.progress}%"

                # Simple progress bar
                progress_bar_length = 20
                filled = int((status.progress / 100) * progress_bar_length)
                bar = "█" * filled + "░" * (progress_bar_length - filled)
                result += f"\nProgress Bar: [{bar}] {status.progress}%"

            if hasattr(status, "start_time"):
                result += f"\nStarted: {status.start_time}"

            if hasattr(status, "message") and status.message:
                result += f"\nMessage: {status.message}"

            # Add monitoring instructions
            if hasattr(status, "status") and status.status.upper() in ["RUNNING", "PENDING"]:
                result += f"""

📊 Job is still {status.status.lower()}. To continue monitoring:
  - Check status again: get_job_status('{execution_id}')
  - For real-time monitoring, check status every {check_interval} seconds
  - Cancel if needed: cancel_job('{execution_id}')"""
            else:
                result += f"\n\n✅ Job monitoring complete. Final status: {status.status}"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error monitoring job: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_monitor_job)
