# mcp_unsplash_photo_search

## Overview

The `mcp_unsplash_photo_search` server provides an MCP interface to search for photos on Unsplash using keywords, filters like color and orientation, and sorting options. It returns structured photo details including URLs for different sizes, descriptions, and dimensions.

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure you have Python 3.10 or higher installed.

## Running the Server

To start the server, run the following command:

```bash
python mcp_unsplash_photo_search.py
```

Make sure the environment variable `UNSPLASH_ACCESS_KEY` is set with a valid Unsplash API access key.

## Available Tools

### `search_photos`

Searches for photos on Unsplash based on the provided criteria.

**Parameters:**
- `query` (str, required): Search keyword(s).
- `page` (int, optional): Page number for paginated results (default: 1).
- `per_page` (int, optional): Number of results per page (1–30, default: 10).
- `order_by` (str, optional): Sorting order (`latest`, `popular`, `relevant`, default: `popular`).
- `color` (str, optional): Filter by color (e.g., `red`, `blue`).
- `orientation` (str, optional): Filter by orientation (`landscape`, `portrait`, `squarish`).

**Returns:**
A list of dictionaries containing:
- `id`: Unique identifier for the photo.
- `description`: Description or alt text.
- `urls`: URLs for different sizes (`raw`, `full`, `regular`, `small`, `thumb`).
- `width`: Width in pixels.
- `height`: Height in pixels.

**Raises:**
- `ValueError`: If parameters are invalid or missing.
- `httpx.HTTPStatusError`: If the API request fails.