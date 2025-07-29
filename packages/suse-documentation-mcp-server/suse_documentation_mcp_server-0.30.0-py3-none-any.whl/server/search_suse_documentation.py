import asyncio
import os
import sys
import time

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

base_url = os.getenv("OI_API_BASE", "") + "/api/v1/retrieval/process/web"
authorization_token = os.getenv("OI_API_TOKEN", "")

# Initialize FastMCP server
mcp = FastMCP(
    "web-search",
    prompt="""
# Web Search MCP Server

This server provides tools for searching the web using Open WebUI Web search API.
It allows you to search web for given search query.

## Available Tools

### 1. get_web_search_results
Use this tool to search web to gather information about SUSE, Rancher products and projects.

Example: "HOw to setup Nvidia GPU in RKE2?" or
"Does Rancher Desktop support Wasm"

## Guidelines for Use

- Always perform a web search even if you think you know the answer
- Use the most relevant and specific keywords for your search
- Keep queries concise and specific for best results

## Output Format

All search results will be formatted as text with clear sections for each
result item, including:

- URL: The link to the source of the information
- Content: A brief summary or excerpt from the page

If the API call fails for any reason, appropriate error messages will be
returned.
""",
)

def clean_content(content):
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n+', '\n\n', content.strip())
    # Replace multiple spaces with a single space
    cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)
    return cleaned_content

def get_web_search_results_from_oi(query):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {authorization_token}'
    }

    # Step 1: Get web search results (list of URLs)
    search_payload = {
        "query": query,
        "collection_name": "your_collection_name"
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
            "url": filename,
            "collection_name": search_data["collection_name"]
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

@mcp.tool()
async def get_web_search_results(
    query: str
) -> str:
    """Performs a web search using the Open WebUI web search API.

    Args:
        query: Search query (required)
    """
  
    try:      
        # Process the query
        result = get_web_search_results_from_oi(query)
        
        return result
    except Exception as e:
        return f"Error performing web search: {str(e)}\n\nQuery: {query}"    

def main():
    """Main entry point for the script."""
    # Initialize and run the server
    print("Starting SUSE Documentation Search Server...")
    mcp.run()
    
if __name__ == "__main__":
    # Initialize and run the server
    main()
    