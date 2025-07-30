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
from .cve import SearchCVEParams, search_cve
from .release import SearchReleaseParams, GetVersionCVEsParams, search_release, get_version_cves
from .release import GetLatestVersionParams, GetSpecificVersionParams, get_latest_version, get_specific_version

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
            Tool(
                name="get_version_cves",
                description="Get CVEs for a specific version of a product. Optionally filter by vendor. Uses caching (TTL: 1 day).",
                inputSchema=GetVersionCVEsParams.model_json_schema(),
            ),
            Tool(
                name="get_latest_version",
                description="Get the latest version information for a product. Optionally filter by vendor.",
                inputSchema=GetLatestVersionParams.model_json_schema(),
            ),
            Tool(
                name="get_specific_version",
                description="Get a specific version of a product. Optionally filter by vendor.",
                inputSchema=GetSpecificVersionParams.model_json_schema(),
            ),
        ]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return []

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        if name == "search_cve":
            return await search_cve(arguments, apikey)
        elif name == "search_release":
            return await search_release(arguments, apikey)
        elif name == "get_version_cves":
            return await get_version_cves(arguments, apikey)
        elif name == "get_latest_version":
            return await get_latest_version(arguments, apikey)
        elif name == "get_specific_version":
            return await get_specific_version(arguments, apikey)
        else:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}"))

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="No prompts available."))

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
