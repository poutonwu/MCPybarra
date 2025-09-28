# mcp_unsplash_photo_search

## Overview

The `mcp_unsplash_photo_search` server provides integration with the Unsplash API to search for photos based on keywords and filters such as color, orientation, and sort order. This MCP server enables large language models (LLMs) to query and retrieve high-quality images from Unsplash programmatically.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following packages:

```
mcp[cli]
httpx
python-dotenv
```

## Running the Server

To run the server, execute the Python script from the command line:

```bash
python mcp_unsplash_photo_search.py
```

Ensure that the `UNSPLASH_ACCESS_KEY` environment variable is set in a `.env` file or directly in your environment:

```
UNSPLASH_ACCESS_KEY=your-unsplash-api-key
```

## Available Tools

### `search_photos`

Searches for photos on Unsplash based on a keyword and optional filters.

#### Parameters:
- `query` (str): Search term (e.g., "nature"). Required.
- `page` (int): Page number for pagination. Default: 1.
- `per_page` (int): Number of results per page. Default: 10.
- `order_by` (str): Sort order — `"relevant"` or `"latest"`. Default: `"relevant"`.
- `color` (str): Filter by color (e.g., `"black_and_white"`, `"blue"`). Optional.
- `orientation` (str): Filter by orientation — `"landscape"`, `"portrait"`, or `"squarish"`. Optional.

#### Returns:
A list of dictionaries containing photo details like ID, description, URLs, width, and height.

#### Example Usage:
```python
search_photos(query="nature", page=1, per_page=10, order_by="latest")
```

#### Raises:
- `ValueError`: If the `query` parameter is empty.
- `RuntimeError`: If there's an issue with the network or the Unsplash API returns an error.