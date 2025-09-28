# mcp_unsplash_search_photos

## Overview

The `mcp_unsplash_search_photos` server provides integration with the Unsplash API, allowing users to search for photos based on keywords and optional filters such as color, orientation, and sort order. This server is implemented using the Model Context Protocol (MCP) and can be used by large language models (LLMs) to fetch relevant images programmatically.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following:

```
mcp[cli]
httpx
```

---

## Running the Server

To run the server, first set the Unsplash API access key as an environment variable:

```bash
export UNSPLASH_ACCESS_KEY='your_unsplash_api_key'
```

Then execute the server script:

```bash
python mcp_unsplash_search_photos.py
```

---

## Available Tools

### `search_photos`

Searches for photos on Unsplash based on a query and optional filters like page number, results per page, sort order, color, and orientation.

#### Parameters:
- `query`: Search keywords (e.g., "dogs", "office desk") *(required)*
- `page`: Page number to retrieve (default: 1)
- `per_page`: Number of items per page (max 30, default: 10)
- `order_by`: Sort order — "latest" or "relevant" (default: "relevant")
- `color`: Color filter (e.g., "blue", "black_and_white")
- `orientation`: Orientation filter — "landscape", "portrait", or "squarish"

#### Returns:
A JSON-formatted string containing a list of photo objects with details like ID, description, dimensions, and image URLs.

#### Example:
```json
[
  {
    "id": "some_photo_id",
    "description": "a cat sitting on a window sill",
    "width": 4000,
    "height": 4000,
    "urls": {
      "raw": "...",
      "full": "...",
      "regular": "...",
      "small": "...",
      "thumb": "..."
    }
  }
]
```