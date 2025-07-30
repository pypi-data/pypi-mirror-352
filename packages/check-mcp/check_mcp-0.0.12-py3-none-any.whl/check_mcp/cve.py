from typing import Optional, List
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, TextContent, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field
import httpx
from .config import Config

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

async def search_cve(arguments: dict, apikey: str) -> list[TextContent]:
    try:
        args = SearchCVEParams(**arguments)
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    params = {k: v for k, v in args.dict().items() if v is not None}
    headers = {"apikey": apikey}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{Config.api.cve_endpoint}/search", params=params, headers=headers, timeout=30)
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
    results = []
    for cve in data:
        results.append(
            f"CVE ID: {cve.get('cve_id', '')}\nState: {cve.get('state', '')}\nPublished: {cve.get('published_date', '')}\nScore: {cve.get('score', '')}\nTitle: {cve.get('title', '')}\nVendor: {cve.get('vendor', '')}\nDescription: {cve.get('description', '')}\nReferences: {', '.join(cve.get('references', []))}\n---"
        )
    return [TextContent(type="text", text="\n\n".join(results))] 