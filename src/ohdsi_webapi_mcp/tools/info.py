"""Tools for WebAPI info and system information."""

import asyncio
import os

import mcp.types as types
from ohdsi_webapi import WebApiClient


async def get_webapi_info() -> list[types.TextContent]:
    """Get WebAPI version and system information.

    Returns
    -------
    List[types.TextContent]
        WebAPI system information formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_get_info():
        client = WebApiClient(webapi_base_url)
        try:
            # Get WebAPI info
            info = client.info.get()

            if not info:
                return [types.TextContent(type="text", text="No WebAPI information available")]

            result = f"""WebAPI System Information:

Base URL: {webapi_base_url}"""

            # Add version information if available
            if hasattr(info, "version"):
                result += f"\nVersion: {info.version}"

            if hasattr(info, "build_info"):
                result += f"\nBuild Info: {info.build_info}"

            if hasattr(info, "database_dialect"):
                result += f"\nDatabase Dialect: {info.database_dialect}"

            # Add any other available fields
            if hasattr(info, "__dict__"):
                other_fields = []
                for key, value in info.__dict__.items():
                    if key not in ["version", "build_info", "database_dialect"] and not key.startswith("_"):
                        other_fields.append(f"{key}: {value}")

                if other_fields:
                    result += "\n\nAdditional Information:"
                    for field in other_fields:
                        result += f"\n  - {field}"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving WebAPI info: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_info)


async def get_webapi_version() -> list[types.TextContent]:
    """Get WebAPI version information.

    Returns
    -------
    List[types.TextContent]
        WebAPI version information formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_get_version():
        client = WebApiClient(webapi_base_url)
        try:
            # Get version info
            if hasattr(client.info, "version"):
                version = client.info.version()
            else:
                # Fall back to general info
                info = client.info.get()
                version = getattr(info, "version", "Unknown")

            result = f"""WebAPI Version Information:

Base URL: {webapi_base_url}
Version: {version}"""

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving WebAPI version: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_version)


async def check_webapi_health() -> list[types.TextContent]:
    """Check WebAPI health and connectivity.

    Returns
    -------
    List[types.TextContent]
        WebAPI health status formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_check_health():
        client = WebApiClient(webapi_base_url)
        try:
            # Try to get basic info as a health check
            info = client.info.get()

            if info:
                result = f"""WebAPI Health Check: ✅ HEALTHY

Base URL: {webapi_base_url}
Status: Connected successfully
Response: Received valid info response"""

                if hasattr(info, "version"):
                    result += f"\nVersion: {info.version}"

            else:
                result = f"""WebAPI Health Check: ⚠️  WARNING

Base URL: {webapi_base_url}
Status: Connected but no info returned
Response: Empty or invalid response"""

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            result = f"""WebAPI Health Check: ❌ FAILED

Base URL: {webapi_base_url}
Status: Connection failed
Error: {str(e)}

Please check:
  - WebAPI URL is correct and accessible
  - WebAPI service is running
  - Network connectivity
  - Authentication if required"""

            return [types.TextContent(type="text", text=result)]
        finally:
            try:
                client.close()
            except Exception:
                pass  # Ignore errors during cleanup

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_check_health)
