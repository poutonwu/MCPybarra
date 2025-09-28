import os
import sys
import json
from pyzotero import zotero
from PyPDF2 import PdfReader
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_zotero_library_manager")

# Environment variables for sensitive information
ZOTERO_LIBRARY_ID=os.getenv('ZOTERO_LIBRARY_ID')
# Zotero 库的类型 ('user' 或 'group')
ZOTERO_LIBRARY_TYPE=os.getenv('ZOTERO_LIBRARY_TYPE')
# 您的 Zotero API 密钥
ZOTERO_API_KEY=os.getenv('ZOTERO_API_KEY')
# 如果使用本地 Zotero 客户端，设置为 "true"
ZOTERO_LOCAL=""

# Validate environment variables
if not ZOTERO_API_KEY or not ZOTERO_LIBRARY_ID or not ZOTERO_LIBRARY_TYPE:
    raise EnvironmentError("Missing required Zotero environment variables.")

# Initialize Zotero client
zot = zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, ZOTERO_API_KEY)

@mcp.tool()
def get_item_metadata(item_key: str) -> str:
    """
    Fetch detailed metadata of a Zotero item using its unique item key.

    Args:
        item_key (str): The unique key identifying the Zotero item.
            Example: "ABC123"

    Returns:
        str: A JSON string containing item metadata, such as title, creators, publication year, and other bibliographic details.
            Example:
            {
                "title": "Sample Title",
                "creators": ["John Doe", "Jane Smith"],
                "year": 2023,
                "publisher": "Sample Publisher",
                "DOI": "10.1234/sample.doi"
            }

    Raises:
        ValueError: If the item key is invalid.
        Exception: If the Zotero API call fails.
    """
    try:
        item = zot.item(item_key)
        metadata = {
            "title": item['data'].get('title', ""),
            "creators": [creator['lastName'] for creator in item['data'].get('creators', [])],
            "year": item['data'].get('date', ""),
            "publisher": item['data'].get('publisher', ""),
            "DOI": item['data'].get('DOI', "")
        }
        return json.dumps(metadata, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def get_item_fulltext(item_key: str) -> str:
    """
    Extract the full text content of a Zotero item. If the item contains a PDF, extract text from the PDF file.

    Args:
        item_key (str): The unique key identifying the Zotero item.
            Example: "ABC123"

    Returns:
        str: A string containing the extracted full text content of the item.
            Example: "This is the extracted full text content of the PDF associated with the Zotero item."

    Raises:
        ValueError: If the item key is invalid or no PDF attachment is found.
        Exception: If the Zotero API call or PDF extraction fails.
    """
    try:
        item = zot.item(item_key)
        attachment_key = None
        for attachment in item['data'].get('attachments', []):
            if attachment.get('contentType') == 'application/pdf':
                attachment_key = attachment.get('key')
                break

        if not attachment_key:
            raise ValueError("No PDF attachment found for the given item key.")

        pdf_path = zot.dump(attachment_key)
        reader = PdfReader(pdf_path)
        full_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return full_text
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def search_items(title: str = None, creators: str = None, year: int = None, fulltext: str = None) -> str:
    """
    Search the Zotero library based on specified criteria and return a list of formatted search results.

    Args:
        title (str, optional): Search by title.
            Example: "Sample Title"
        creators (str, optional): Search by creators.
            Example: "John Doe"
        year (int, optional): Search by publication year.
            Example: 2023
        fulltext (str, optional): Perform a full-text search.
            Example: "Keyword"

    Returns:
        str: A JSON string containing a list of dictionaries, each containing metadata for a matching item.
            Example:
            [
                {
                    "title": "Sample Title",
                    "creators": ["John Doe", "Jane Smith"],
                    "year": 2023,
                    "DOI": "10.1234/sample.doi"
                },
                {
                    "title": "Another Title",
                    "creators": ["Alice Johnson"],
                    "year": 2022,
                    "DOI": "10.5678/another.doi"
                }
            ]

    Raises:
        Exception: If the Zotero API call fails.
    """
    try:
        query_params = {}
        if title:
            query_params['q'] = title
        if creators:
            query_params['creator'] = creators
        if year:
            query_params['year'] = year
        if fulltext:
            query_params['fulltext'] = fulltext

        zot.add_parameters(**query_params)
        items = zot.top(limit=10)
        results = []
        for item in items:
            results.append({
                "title": item['data'].get('title', ""),
                "creators": [creator['lastName'] for creator in item['data'].get('creators', [])],
                "year": item['data'].get('date', ""),
                "DOI": item['data'].get('DOI', "")
            })
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()