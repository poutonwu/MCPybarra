import os
import sys
import json
import io
from mcp.server.fastmcp import FastMCP
from pyzotero import zotero
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration Management ---
# Retrieve Zotero credentials from environment variables
ZOTERO_LIBRARY_ID = os.environ.get('ZOTERO_LIBRARY_ID', "16026771")
ZOTERO_API_KEY = os.environ.get('ZOTERO_API_KEY', "goIOXCQJi4LP4WIZbJlpb4Ve")
ZOTERO_LIBRARY_TYPE = os.environ.get('ZOTERO_LIBRARY_TYPE', 'user')  # Default to 'user'

# --- Proxy Support ---
# Set proxy if defined in environment variables
HTTP_PROXY = os.environ.get('HTTP_PROXY')
HTTPS_PROXY = os.environ.get('HTTPS_PROXY')
if HTTP_PROXY:
    os.environ['HTTP_PROXY'] = HTTP_PROXY
if HTTPS_PROXY:
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY

# Initialize FastMCP Server
mcp = FastMCP("mcp_zotero_library_manager")

# --- Zotero Client Initialization ---
# Ensure all required environment variables are set
if not all([ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, ZOTERO_LIBRARY_TYPE]):
    raise ValueError("Missing required Zotero credentials in environment variables (ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, ZOTERO_LIBRARY_TYPE)")

try:
    zot = zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, ZOTERO_API_KEY)
except Exception as e:
    raise ConnectionError(f"Failed to connect to Zotero API: {e}")

@mcp.tool()
def get_item_metadata(item_key: str) -> str:
    """Retrieves the complete metadata for a single item in the Zotero library using its unique item key.

    This function fetches all available metadata for a given Zotero item,
    including title, authors, publication date, abstract, tags, and other
    bibliographic details. The result is returned as a formatted JSON string.

    Args:
        item_key (str): The unique identifier for the Zotero item.
                        Example: "ABCDE123"

    Returns:
        str: A JSON string containing the detailed metadata of the specified
             Zotero item. If the item is not found, an error will be raised.
    """
    if not isinstance(item_key, str) or not item_key.strip():
        raise ValueError("Parameter 'item_key' must be a non-empty string.")

    try:
        item = zot.item(item_key)
        if not item:
            raise FileNotFoundError(f"No item found with key: {item_key}")
        return json.dumps(item, indent=2)
    except Exception as e:
        # Catch potential API errors or other issues
        raise RuntimeError(f"An error occurred while fetching item metadata: {e}")

@mcp.tool()
def get_item_fulltext(item_key: str) -> str:
    """Extracts and returns the full text content from the primary PDF attachment of a specified Zotero item.

    This function locates the first PDF attachment associated with the given
    Zotero item key, downloads it, and extracts all text content from its pages.
    It is useful for obtaining the complete text of an article or document for
    analysis or summarization.

    Args:
        item_key (str): The unique identifier for the Zotero item.
                        Example: "ABCDE123"

    Returns:
        str: A string containing the complete, extracted plain text from the
             item's PDF attachment. Returns a message if no PDF attachment
             or full text is available.
    """
    if not isinstance(item_key, str) or not item_key.strip():
        raise ValueError("Parameter 'item_key' must be a non-empty string.")

    try:
        attachments = zot.children(item_key)
        pdf_attachment = None
        for attachment in attachments:
            if attachment['data'].get('contentType') == 'application/pdf':
                pdf_attachment = attachment
                break

        if not pdf_attachment:
            return "No PDF attachment found for this item."

        # Download the PDF file content
        pdf_content = zot.file(pdf_attachment['key'])

        if not pdf_content:
            return "Could not retrieve PDF content."

        # Extract text from the PDF
        text = ""
        with io.BytesIO(pdf_content) as pdf_file:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as pdf_error:
                raise RuntimeError(f"Failed to read or extract text from PDF: {pdf_error}")

        return text.strip() if text.strip() else "No text could be extracted from the PDF."

    except Exception as e:
        raise RuntimeError(f"An error occurred while extracting full text: {e}")

@mcp.tool()
def search_items(query: str, search_field: str = 'everything', limit: int = 25) -> str:
    """Performs a flexible search within the Zotero library and returns key metadata.

    This function searches the Zotero library based on a query string. It can
    search across all fields ('everything') or be restricted to specific fields
    like 'title', 'creator' (author), or 'year'. The results are formatted
    into a concise JSON list, each entry containing the item key, title,
    creators, and publication year.

    Args:
        query (str): The search term or phrase to look for.
                     Example: "machine learning"
        search_field (str, optional): The specific field to search within.
                                      Accepted values are 'title', 'creator',
                                      'year', or 'everything'.
                                      Defaults to 'everything'.
                                      Example: "title"
        limit (int, optional): The maximum number of search results to return.
                               Defaults to 25.
                               Example: 50

    Returns:
        str: A JSON string representing a list of found Zotero items with their
             key metadata. Returns an empty list if no items are found.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Parameter 'query' must be a non-empty string.")
    if search_field not in ['title', 'creator', 'year', 'everything']:
        raise ValueError("Parameter 'search_field' must be one of 'title', 'creator', 'year', or 'everything'.")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Parameter 'limit' must be a positive integer.")

    try:
        # Pyzotero's 'q' parameter performs a broad search.
        # 'everything' mode searches full-text content as well.
        # 'titleCreatorYear' searches only in those specific metadata fields.
        qmode = 'everything' if search_field == 'everything' else 'titleCreatorYear'

        # For specific field searches, we can use the 'itemType' parameter with a filter
        # However, for title, creator, and year, 'q' with 'titleCreatorYear' is the
        # standard approach. Zotero API doesn't have a direct filter for 'creator' or 'year'
        # in the main 'items' endpoint, so we rely on the query matching.
        results = zot.items(q=query, qmode=qmode, limit=limit)

        # Post-filter if a specific field was requested, as 'q' can be broad
        filtered_results = []
        if search_field in ['title', 'creator', 'year']:
            for item in results:
                data = item.get('data', {})
                match = False
                if search_field == 'title' and query.lower() in data.get('title', '').lower():
                    match = True
                elif search_field == 'year' and query in data.get('date', ''):
                    match = True
                elif search_field == 'creator':
                    creators = data.get('creators', [])
                    for c in creators:
                        if query.lower() in c.get('firstName', '').lower() or query.lower() in c.get('lastName', '').lower():
                            match = True
                            break
                if match:
                    filtered_results.append(item)
            results = filtered_results
        
        formatted_results = []
        for item in results:
            data = item.get('data', {})
            creators_list = [f"{c.get('firstName', '')} {c.get('lastName', '')}".strip()
                             for c in data.get('creators', []) if c.get('creatorType') == 'author']
            creators = ", ".join(filter(None, creators_list))

            formatted_item = {
                "item_key": data.get('key'),
                "title": data.get('title'),
                "creators": creators,
                "year": data.get('date', '').split('-')[0] if data.get('date') else None
            }
            formatted_results.append(formatted_item)

        return json.dumps(formatted_results, indent=2)

    except Exception as e:
        raise RuntimeError(f"An error occurred during the search operation: {e}")

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()