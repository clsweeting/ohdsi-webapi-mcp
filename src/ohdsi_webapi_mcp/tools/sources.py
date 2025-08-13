"""Tools for WebAPI data sources management."""

import asyncio
import os

import mcp.types as types
from ohdsi_webapi import WebApiClient


async def list_data_sources() -> list[types.TextContent]:
    """List all available data sources in the WebAPI.

    Returns
    -------
    List[types.TextContent]
        List of data sources formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_list_sources():
        client = WebApiClient(webapi_base_url)
        try:
            sources = client.sources.list()

            if not sources:
                return [types.TextContent(type="text", text="No data sources found")]

            result = f"Available Data Sources ({len(sources)} total):\n\n"

            for source in sources:
                # Format source info
                source_info = f"• {source.source_name} (Key: {source.source_key})"

                if hasattr(source, "source_dialect") and source.source_dialect:
                    source_info += f"\n  Dialect: {source.source_dialect}"

                if hasattr(source, "source_connection") and source.source_connection:
                    source_info += f"\n  Connection: {source.source_connection}"

                if hasattr(source, "cdm_version") and source.cdm_version:
                    source_info += f"\n  CDM Version: {source.cdm_version}"

                if hasattr(source, "vocabulary_version") and source.vocabulary_version:
                    source_info += f"\n  Vocabulary Version: {source.vocabulary_version}"

                # Add priority and other attributes
                if hasattr(source, "source_priority") and source.source_priority is not None:
                    source_info += f"\n  Priority: {source.source_priority}"

                result += source_info + "\n\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving data sources: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_list_sources)


async def get_source_details(source_key: str) -> list[types.TextContent]:
    """Get detailed information about a specific data source.

    Parameters
    ----------
    source_key : str
        The source key to retrieve details for.

    Returns
    -------
    List[types.TextContent]
        Data source details formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_get_source_details():
        client = WebApiClient(webapi_base_url)
        try:
            # Get all sources and find the one matching the key
            sources = client.sources.list()

            source = None
            for s in sources:
                if s.source_key == source_key:
                    source = s
                    break

            if not source:
                return [types.TextContent(type="text", text=f"No data source found with key: {source_key}")]

            result = f"""Data Source Details for '{source_key}':

Name: {source.source_name}
Key: {source.source_key}"""

            # Add all available source attributes
            if hasattr(source, "source_dialect") and source.source_dialect:
                result += f"\nDialect: {source.source_dialect}"

            if hasattr(source, "source_connection") and source.source_connection:
                result += f"\nConnection: {source.source_connection}"

            if hasattr(source, "cdm_version") and source.cdm_version:
                result += f"\nCDM Version: {source.cdm_version}"

            if hasattr(source, "vocabulary_version") and source.vocabulary_version:
                result += f"\nVocabulary Version: {source.vocabulary_version}"

            if hasattr(source, "source_priority") and source.source_priority is not None:
                result += f"\nPriority: {source.source_priority}"

            if hasattr(source, "source_release_date") and source.source_release_date:
                result += f"\nRelease Date: {source.source_release_date}"

            if hasattr(source, "cdm_holder") and source.cdm_holder:
                result += f"\nCDM Holder: {source.cdm_holder}"

            if hasattr(source, "source_description") and source.source_description:
                result += f"\nDescription: {source.source_description}"

            if hasattr(source, "source_documentation_reference") and source.source_documentation_reference:
                result += f"\nDocumentation: {source.source_documentation_reference}"

            # Add any other fields if available
            if hasattr(source, "__dict__"):
                other_fields = []
                shown_fields = {
                    "source_name",
                    "source_key",
                    "source_dialect",
                    "source_connection",
                    "cdm_version",
                    "vocabulary_version",
                    "source_priority",
                    "source_release_date",
                    "cdm_holder",
                    "source_description",
                    "source_documentation_reference",
                }

                for key, value in source.__dict__.items():
                    if key not in shown_fields and not key.startswith("_") and value is not None:
                        other_fields.append(f"{key}: {value}")

                if other_fields:
                    result += "\n\nAdditional Information:"
                    for field in other_fields[:10]:  # Limit to avoid overwhelming output
                        result += f"\n  - {field}"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving source details: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_source_details)


async def get_default_source() -> list[types.TextContent]:
    """Get information about the default data source.

    Returns
    -------
    List[types.TextContent]
        Default source information formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    webapi_source_key = os.getenv("WEBAPI_SOURCE_KEY")

    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_get_default_source():
        client = WebApiClient(webapi_base_url)
        try:
            sources = client.sources.list()

            if not sources:
                return [types.TextContent(type="text", text="No data sources available")]

            result = "Default Data Source Information:\n\n"

            if webapi_source_key:
                # Look for the specified source key
                default_source = None
                for source in sources:
                    if source.source_key == webapi_source_key:
                        default_source = source
                        break

                if default_source:
                    result += "Configured Source (from WEBAPI_SOURCE_KEY):\n"
                    result += f"  - Name: {default_source.source_name}\n"
                    result += f"  - Key: {default_source.source_key}\n"
                    if hasattr(default_source, "source_dialect"):
                        result += f"  - Dialect: {default_source.source_dialect}\n"
                    if hasattr(default_source, "cdm_version"):
                        result += f"  - CDM Version: {default_source.cdm_version}\n"
                else:
                    result += f"⚠️  Configured source key '{webapi_source_key}' not found!\n\n"
                    result += "Available sources:\n"
                    for source in sources[:5]:  # Show first 5
                        result += f"  - {source.source_name} (Key: {source.source_key})\n"
            else:
                # Show the first available source as default
                default_source = sources[0]
                result += "No WEBAPI_SOURCE_KEY configured. First available source:\n"
                result += f"  - Name: {default_source.source_name}\n"
                result += f"  - Key: {default_source.source_key}\n"
                if hasattr(default_source, "source_dialect"):
                    result += f"  - Dialect: {default_source.source_dialect}\n"
                if hasattr(default_source, "cdm_version"):
                    result += f"  - CDM Version: {default_source.cdm_version}\n"

                result += "\nTo set a default source, configure WEBAPI_SOURCE_KEY environment variable.\n"

                if len(sources) > 1:
                    result += f"\nOther available sources ({len(sources) - 1}):\n"
                    for source in sources[1:6]:  # Show next 5
                        result += f"  - {source.source_name} (Key: {source.source_key})\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving default source: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_default_source)
