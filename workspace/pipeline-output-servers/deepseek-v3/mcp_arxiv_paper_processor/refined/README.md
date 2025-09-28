# mcp_arxiv_paper_processor

## Overview

`mcp_arxiv_paper_processor` is an MCP server that provides tools for searching, downloading, listing, and reading academic papers from arXiv. It allows integration with large language models (LLMs) via the Model Context Protocol (MCP), enabling seamless access to arXiv research content.

## Installation

To install dependencies:

1. Ensure Python 3.10+ is installed.
2. Install the required packages using pip:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
httpx
arxiv
PyPDF2
```

## Running the Server

Run the server using the following command:

```bash
python mcp_arxiv_paper_processor.py
```

This starts the MCP server using standard input/output transport by default.

## Available Tools

### `search_papers`

**Description:** Searches arXiv for academic papers based on a provided query.

**Args:**
- `query`: Search query string (e.g., "machine learning").
- `max_results`: Maximum number of results to return (default: 5).

**Returns:** A JSON string containing a list of dictionaries with paper metadata (title, authors, arXiv ID, abstract).

---

### `download_paper`

**Description:** Downloads the PDF of a specified arXiv paper and saves it locally.

**Args:**
- `paper_id`: The arXiv ID of the paper (e.g., "2307.12345").
- `save_path`: Local directory path to save the PDF (default: "./papers").

**Returns:** A JSON string with a success/failure message and the local file path.

---

### `list_papers`

**Description:** Lists all locally stored papers, optionally filtered by a query.

**Args:**
- `query`: Optional filter string to match against paper IDs.

**Returns:** A JSON string containing a list of dictionaries with local paper details (arXiv ID, file path, download time).

---

### `read_paper`

**Description:** Reads the content of a specified locally stored paper.

**Args:**
- `paper_id`: The arXiv ID or local filename of the paper.
- `mode`: Either `"text"` for raw text extraction or `"metadata"` for structured data (default: `"text"`).

**Returns:** A JSON string with either the full text of the paper or its metadata.