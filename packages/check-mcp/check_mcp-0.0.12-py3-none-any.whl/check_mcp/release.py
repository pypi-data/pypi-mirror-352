from typing import Optional, List
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, TextContent, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field
import httpx
from .config import Config

class SearchReleaseParams(BaseModel):
    vendor: Optional[str] = Field(None, description="Optional vendor name to filter by (case-insensitive)")
    product_name: Optional[str] = Field(None, description="Optional product name to filter by (case-insensitive)")
    from_date: Optional[str] = Field(None, description="Optional start date (inclusive) for filtering (YYYY-MM-DD or ISO datetime)")
    to_date: Optional[str] = Field(None, description="Optional end date (inclusive) for filtering (YYYY-MM-DD or ISO datetime)")
    date_field: Optional[str] = Field("release_date", description='Which date field to filter on (e.g., "release_date")')
    page: Optional[int] = Field(1, description="Page number (starting from 1)")
    page_size: Optional[int] = Field(100, description="Number of items per page")

class GetVersionCVEsParams(BaseModel):
    product_name: str = Field(..., description="Product name (e.g., 'nginx')")
    version: str = Field(..., description="Specific version to retrieve CVEs for (e.g., '1.0.0')")
    vendor: Optional[str] = Field(None, description="Optional vendor name to filter by (case-insensitive)")

class GetLatestVersionParams(BaseModel):
    product_name: str = Field(..., description="Product name (e.g., 'nginx')")
    vendor: Optional[str] = Field(None, description="Optional vendor name to filter by (case-insensitive)")

class GetSpecificVersionParams(BaseModel):
    product_name: str = Field(..., description="Product name (e.g., 'nginx')")
    version: str = Field(..., description="Specific version to retrieve (e.g., '1.0.0')")
    vendor: Optional[str] = Field(None, description="Optional vendor name to filter by (case-insensitive)")

async def search_release(arguments: dict, apikey: str) -> list[TextContent]:
    try:
        args = SearchReleaseParams(**arguments)
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    params = {k: v for k, v in args.dict().items() if v is not None}
    headers = {"apikey": apikey}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{Config.api.release_endpoint}/search", params=params, headers=headers, timeout=30)
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
    results = []
    for rel in data:
        results.append(
            f"Product: {rel.get('product_name', '')}\nVendor: {rel.get('vendor', '')}\nVersion: {rel.get('version', '')}\nRelease Date: {rel.get('release_date', '')}\nActive Support End: {rel.get('active_support_end_date', '')}\nSecurity Support End: {rel.get('security_support_end_date', '')}\nEOL: {rel.get('eol_date', '')}\n---"
        )
    return [TextContent(type="text", text="\n\n".join(results))]

async def get_version_cves(arguments: dict, apikey: str) -> list[TextContent]:
    try:
        args = GetVersionCVEsParams(**arguments)
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    product_name = args.product_name
    version = args.version
    vendor = args.vendor
    headers = {"apikey": apikey}
    endpoint = f"{Config.api.release_endpoint}/{product_name}/{version}/cves"
    params = {}
    if vendor:
        params["vendor"] = vendor
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(endpoint, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to query Version CVEs API: {e}"))
        try:
            data = resp.json()
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Invalid JSON from Version CVEs API: {e}"))
    if not isinstance(data, list):
        raise McpError(ErrorData(code=INTERNAL_ERROR, message="Unexpected response format from Version CVEs API"))
    if not data:
        return [TextContent(type="text", text="No CVEs found for the given product version.")]
    results = []
    for cve in data:
        results.append(
            f"CVE ID: {cve.get('cve_id', '')}\nState: {cve.get('state', '')}\nPublished: {cve.get('published_date', '')}\nScore: {cve.get('score', '')}\nTitle: {cve.get('title', '')}\nVendor: {cve.get('vendor', '')}\nDescription: {cve.get('description', '')}\nReferences: {', '.join(cve.get('references', []))}\n---"
        )
    return [TextContent(type="text", text="\n\n".join(results))]

async def get_latest_version(arguments: dict, apikey: str) -> list[TextContent]:
    try:
        args = GetLatestVersionParams(**arguments)
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    product_name = args.product_name
    vendor = args.vendor
    headers = {"apikey": apikey}
    endpoint = f"{Config.api.release_endpoint}/{product_name}/latest"
    params = {}
    if vendor:
        params["vendor"] = vendor
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(endpoint, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to query Latest Version API: {e}"))
        try:
            data = resp.json()
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Invalid JSON from Latest Version API: {e}"))
    if not data:
        return [TextContent(type="text", text="No latest version found for the given product.")]
    return [TextContent(type="text", text=str(data))]

async def get_specific_version(arguments: dict, apikey: str) -> list[TextContent]:
    try:
        args = GetSpecificVersionParams(**arguments)
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    product_name = args.product_name
    version = args.version
    vendor = args.vendor
    headers = {"apikey": apikey}
    endpoint = f"{Config.api.release_endpoint}/{product_name}/{version}"
    params = {}
    if vendor:
        params["vendor"] = vendor
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(endpoint, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to query Specific Version API: {e}"))
        try:
            data = resp.json()
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Invalid JSON from Specific Version API: {e}"))
    if not data:
        return [TextContent(type="text", text="No version found for the given product and version.")]
    return [TextContent(type="text", text=str(data))] 