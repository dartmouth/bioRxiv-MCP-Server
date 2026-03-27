import os
from typing import Any, List, Dict, Optional
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from biorxiv_web_search import search_key_words, search_advanced, doi_get_biorxiv_metadata

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read configuration from environment
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")
MCP_HOST = os.environ.get("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.environ.get("MCP_PORT", "8000"))

# Initialize FastMCP server with host/port for HTTP transports
mcp = FastMCP("biorxiv", host=MCP_HOST, port=MCP_PORT)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return JSONResponse({"status": "healthy", "service": "biorxiv-mcp"})


@mcp.tool()
async def search_biorxiv_key_words(key_words: str, num_results: int = 10) -> List[Dict[str, Any]]:
    logging.info(f"Searching for articles with key words: {key_words}, num_results: {num_results}")
    """
    Search for articles on bioRxiv using key words.

    Args:
        key_words: Search query string
        num_results: Number of results to return (default: 10)

    Returns:
        List of dictionaries containing article information
    """
    try:
        results = await asyncio.to_thread(search_key_words, key_words, num_results)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching: {str(e)}"}]

@mcp.tool()
async def search_biorxiv_advanced(
    term: Optional[str] = None,
    title: Optional[str] = None,
    author1: Optional[str] = None,
    author2: Optional[str] = None,
    abstract_title: Optional[str] = None,
    text_abstract_title: Optional[str] = None,
    section: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_results: int = 10
) -> List[Dict[str, Any]]:
    logging.info(f"Performing advanced search with parameters: {locals()}")
    """
    Perform an advanced search for articles on bioRxiv.

    Args:
        term: General search term
        title: Search in title
        author1: First author
        author2: Second author
        abstract_title: Search in abstract and title
        text_abstract_title: Search in full text, abstract, and title
        section: Section of bioRxiv
        start_date: Start date for search range (format: YYYY-MM-DD)
        end_date: End date for search range (format: YYYY-MM-DD)
        num_results: Number of results to return (default: 10)

    Returns:
        List of dictionaries containing article information
    """
    try:
        results = await asyncio.to_thread(
            search_advanced,
            term, title, author1, author2, abstract_title, text_abstract_title,
            section, start_date, end_date, num_results
        )
        return results
    except Exception as e:
        return [{"error": f"An error occurred while performing advanced search: {str(e)}"}]

@mcp.tool()
async def get_biorxiv_metadata(doi: str) -> Dict[str, Any]:
    logging.info(f"Fetching metadata for DOI: {doi}")
    """
    Fetch metadata for a bioRxiv article using its DOI.

    Args:
        doi: DOI of the article

    Returns:
        Dictionary containing article metadata
    """
    try:
        metadata = await asyncio.to_thread(doi_get_biorxiv_metadata, doi)
        return metadata if metadata else {"error": f"No metadata found for DOI: {doi}"}
    except Exception as e:
        return {"error": f"An error occurred while fetching metadata: {str(e)}"}

if __name__ == "__main__":
    logging.info(
        f"Starting bioRxiv MCP server (transport={MCP_TRANSPORT}, host={MCP_HOST}, port={MCP_PORT})"
    )
    mcp.run(transport=MCP_TRANSPORT)
