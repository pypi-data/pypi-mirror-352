import requests
import os
import re
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

base_url = os.getenv("OI_API_BASE", "") + "/api/v1/retrieval/process/web"
authorization_token = os.getenv("OI_API_TOKEN", "")

def clean_content(content):
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n+', '\n\n', content.strip())
    # Replace multiple spaces with a single space
    cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)
    return cleaned_content

def get_web_search_results_from_oi(query):
    
    if not base_url or not authorization_token:
        return (
            "Error: OI_API_BASE and/or  not OI_API_TOKEN not set. Please set the "
            "environment variables."
        )
        
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {authorization_token}'
    }

    # Step 1: Get web search results (list of URLs)
    search_payload = {
        "queries": [query]
    }

    print("Inside get_web_search_results_from_oi:", query)
    search_response = requests.post(f"{base_url}/search", headers=headers, json=search_payload)
    if search_response.status_code != 200:
        raise Exception(f"Search API call failed: {search_response.status_code} - {search_response.text}")

    search_data = search_response.json()

    if not search_data.get("status"):
        raise Exception(f"Search API response indicates failure: {search_data}")

    filenames = search_data.get("filenames", [])
    if not filenames:
        return "No filenames found in the search response."

    combined_response = ""

    # Step 2: Loop through URLs to get page content
    for filename in filenames:
        process_payload = {
            "url": filename
        }

        process_response = requests.post(base_url, headers=headers, json=process_payload)
        if process_response.status_code != 200:
            print(f"Failed to process URL {filename}: {process_response.status_code} - {process_response.text}")
            continue

        process_data = process_response.json()
        if not process_data.get("status"):
            print(f"Processing failed for URL {filename}: {process_data}")
            continue

        content = process_data.get("file", {}).get("data", {}).get("content", "No content available")

        # Append to get combined response
        cleaned_content = clean_content(content)
        combined_response += f"Source: {filename}\n\nContent:\n{cleaned_content}\n\n"

    return combined_response

# Initialize FastMCP server
mcp = FastMCP(
    "open-webui-web-search",
    prompt="""
# Open WebUI Search MCP Server

This server provides tools for searching the web using Microsoft Open WebUI's API.
It allows you to search for web pages, news articles, and images.

## Available Tools

### 1. open_webui_web_search
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

@mcp.tool()
async def get_web_search_results_from_oi(
    query: str, count: int = 10, offset: int = 0, market: str = "en-US"
) -> str:
    """Performs a web search using the Open WebUI Web Search API for general information
    and websites.

    Args:
        query: Search query (required)
    """

    try:       
        # Process the query
        return get_web_search_results_from_oi(query)
    except Exception as e:
        return f"Error performing web search: {str(e)}\n\nPayload: {query}"    

def main():
    """Main entry point for the script."""
    # Initialize and run the server
    mcp.run()
    
if __name__ == "__main__":
    main()
    