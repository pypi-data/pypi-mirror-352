import httpx
import os
import re
from urllib.parse import urlparse
from dotenv import load_dotenv
from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

load_dotenv()

base_url = os.getenv("WEB_SEARCH_API_BASE", "")
acceptable_domains = ["suse.com", "rancherdesktop.io"]

# Initialize FastMCP server
mcp = FastMCP(
    "web-search",
    prompt="""
# Web Search MCP Server

This server provides tools for searching the web using SearXNG API.
It allows you to search for web pages, news articles, and images.

## Available Tools

### 1. web_search
Use this tool for general web searches. Best for finding information,
websites, articles, and general content.

Example: "What is the capital of France?" or
"recipe for chocolate chip cookies"

## Guidelines for Use

- Keep queries concise and specific for best results

## Output Format

All search results will be formatted as text with clear sections for each
result item, including:

- Web search: Title, URL, and Description

If the API key is missing or invalid, appropriate error messages will be
returned.
""",
)    

def clean_content(content):
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n+', '\n\n', content.strip())
    # Replace multiple spaces with a single space
    cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)
    return cleaned_content

def safe_get(data, keys, default="No content available"):
    for key in keys:
        data = data.get(key, {})
        if not isinstance(data, dict):
            return default
    return data if data else default

def get_main_domain(hostname):
    parts = hostname.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return hostname

def filter_urls_by_domains(response, acceptable_domains):
    filtered_urls = set()
    for result in response['results']:
        url = result.get('url')
        if url:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            domain = get_main_domain(hostname)
            if domain in acceptable_domains:
                filtered_urls.add(url)

    return list(filtered_urls)
def url_to_markdown(url: str) -> str:
    try:
        md_converter = MarkItDown()
        result = md_converter.convert_url(url)
        return result.text_content
    except Exception as e:
        return f"Error converting content to Markdown: {e}"

@mcp.tool()
async def get_web_search_results(query: str) -> str:
    """Performs a web search using the SearXNG Web Search API for general information
    and websites.

    Args:
        query: Search query (required)
    """
    if not base_url:
        return (
            "Error: WEB_SEARCH_API_BASE not set. Please set the "
            "environment variable."
        )

    # Step 1: Get web search results (list of URLs)
    search_payload = {
        "q": query,
        "format": "json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            try:
                search_response = await client.get(f"{base_url}/search", params=search_payload)
            except httpx.RequestError as e:
                return f"Network error occurred while making the search API call: {str(e)}"
            if search_response.status_code != 200:
                raise Exception(f"Search API call failed: {search_response.status_code} - {search_response.text}")

            search_data = search_response.json()
            filtered_urls = filter_urls_by_domains(search_data, acceptable_domains)
            combined_response = ""

            # Step 2: Loop through URLs to get page content
            for url in filtered_urls[:5]:
                # Append to get combined response
                markdown_content = url_to_markdown(url)
                combined_response += f"Source: {url}\n\nContent:\n{markdown_content}\n\n"

        return combined_response
    except Exception as e:
        return f"Unexpected error: {str(e)}\n\nPayload: {query}"

def main():
    """Main entry point for the script."""
    # Initialize and run the server
    mcp.run()
    
if __name__ == "__main__":
    main()
    