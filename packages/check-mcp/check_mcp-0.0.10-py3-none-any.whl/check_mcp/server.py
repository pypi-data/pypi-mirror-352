from typing import Optional, List
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    GetPromptResult,
    Prompt,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field
import httpx


class SearchCVEParams(BaseModel):
    cve_id: Optional[str] = Field(None, description="Optional CVE ID to search for")
    title: Optional[str] = Field(None, description="Optional title to search in CVE description")
    state: Optional[str] = Field(None, description="Optional state to filter by")
    priority: Optional[str] = Field(None, description="Optional priority level to filter by")
    severity: Optional[str] = Field(None, description="Optional severity level to filter by")
    score: Optional[float] = Field(None, description="Optional CVSS score to filter by")
    product_name: Optional[str] = Field(None, description="Optional product name to filter affected products")
    product_version: Optional[str] = Field(None, description="Optional product version to filter affected products")
    vendor: Optional[str] = Field(None, description="Optional vendor name to filter affected products")
    from_date: Optional[str] = Field(None, description="Optional start date for filtering (YYYY-MM-DD or ISO 8601)")
    to_date: Optional[str] = Field(None, description="Optional end date for filtering (YYYY-MM-DD or ISO 8601)")
    skip: Optional[int] = Field(0, description="Number of records to skip (pagination)")
    limit: Optional[int] = Field(100, description="Maximum number of records to return (pagination)")


class SearchReleaseParams(BaseModel):
    vendor: Optional[str] = Field(None, description="Optional vendor name to filter by (case-insensitive)")
    product_name: Optional[str] = Field(None, description="Optional product name to filter by (case-insensitive)")
    from_date: Optional[str] = Field(None, description="Optional start date (inclusive) for filtering (YYYY-MM-DD or ISO datetime)")
    to_date: Optional[str] = Field(None, description="Optional end date (inclusive) for filtering (YYYY-MM-DD or ISO datetime)")
    date_field: Optional[str] = Field("release_date", description='Which date field to filter on (e.g., "release_date")')
    page: Optional[int] = Field(1, description="Page number (starting from 1)")
    page_size: Optional[int] = Field(100, description="Number of items per page")


async def serve(
    apikey: str = "SPK1HgBWcxO5EmLsCSP6aIRNhX6wXMYa",
) -> None:
    """Run the check MCP server.

    Args:
        apikey: API key to use for requests (default: SPK1HgBWcxO5EmLsCSP6aIRNhX6wXMYa)
    """
    server = Server("mcp-check")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_cve",
                description="Search CVEs with various filters via the Opsify API.",
                inputSchema=SearchCVEParams.model_json_schema(),
            ),
            Tool(
                name="search_release",
                description="Search releases with optional filters for vendor, product name, and date range. Supports pagination.",
                inputSchema=SearchReleaseParams.model_json_schema(),
            ),
        ]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return []

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        if name == "search_cve":
            try:
                args = SearchCVEParams(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
            params = {k: v for k, v in args.dict().items() if v is not None}
            headers = {"apikey": apikey}
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.get("https://api.opsify.dev/checks/cve/search", params=params, headers=headers, timeout=30)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to query CVE API: {e}"))
                try:
                    data = resp.json()
                except Exception as e:
                    raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Invalid JSON from CVE API: {e}"))
            if not isinstance(data, list):
                raise McpError(ErrorData(code=INTERNAL_ERROR, message="Unexpected response format from CVE API"))
            if not data:
                return [TextContent(type="text", text="No CVEs found for the given criteria.")]
            # Format the results for display
            results = []
            for cve in data:
                results.append(
                    f"CVE ID: {cve.get('cve_id', '')}\nState: {cve.get('state', '')}\nPublished: {cve.get('published_date', '')}\nScore: {cve.get('score', '')}\nTitle: {cve.get('title', '')}\nVendor: {cve.get('vendor', '')}\nDescription: {cve.get('description', '')}\nReferences: {', '.join(cve.get('references', []))}\n---"
                )
            return [TextContent(type="text", text="\n\n".join(results))]
        elif name == "search_release":
            try:
                args = SearchReleaseParams(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
            params = {k: v for k, v in args.dict().items() if v is not None}
            headers = {"apikey": apikey}
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.get("https://api.opsify.dev/checks/release/search", params=params, headers=headers, timeout=30)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to query Release API: {e}"))
                try:
                    data = resp.json()
                except Exception as e:
                    raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Invalid JSON from Release API: {e}"))
            if not isinstance(data, list):
                raise McpError(ErrorData(code=INTERNAL_ERROR, message="Unexpected response format from Release API"))
            if not data:
                return [TextContent(type="text", text="No releases found for the given criteria.")]
            # Format the results for display
            results = []
            for rel in data:
                results.append(
                    f"Product: {rel.get('product_name', '')}\nVendor: {rel.get('vendor', '')}\nVersion: {rel.get('version', '')}\nRelease Date: {rel.get('release_date', '')}\nActive Support End: {rel.get('active_support_end_date', '')}\nSecurity Support End: {rel.get('security_support_end_date', '')}\nEOL: {rel.get('eol_date', '')}\n---"
                )
            return [TextContent(type="text", text="\n\n".join(results))]
        else:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}"))

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="No prompts available."))

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
