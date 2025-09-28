# mcp_pdf_toolkit

## Overview
`mcp_pdf_toolkit` is a Model Context Protocol (MCP) server that provides a set of tools for working with PDF files. It allows you to merge, extract pages from, search for, and find related PDF documents using content similarity.

This server enables seamless integration with large language models (LLMs), allowing them to interact with PDF files programmatically through the MCP protocol.

## Installation

1. Ensure Python 3.10+ is installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Make sure your `requirements.txt` includes:
```
mcp[cli]
pypdf
thefuzz
scikit-learn
```

## Running the Server

To start the server, run the following command:
```bash
python mcp_pdf_toolkit.py
```

Ensure that the server script file is named `mcp_pdf_toolkit.py` or adjust the command accordingly.

## Available Tools

### `merge_pdfs`
**Description:** Merges multiple specified PDF files into a single PDF file.

**Arguments:**
- `pdf_paths`: List of full paths to the PDF files to be merged.
- `output_path`: Full path where the merged PDF will be saved.

---

### `extract_pages`
**Description:** Extracts specified pages from a source PDF and creates a new PDF file.

**Arguments:**
- `source_path`: Full path to the source PDF file.
- `pages`: List of page numbers (0-indexed) to extract.
- `output_path`: Full path where the extracted pages will be saved.

---

### `search_pdfs`
**Description:** Searches for PDF files in a given directory matching a glob pattern.

**Arguments:**
- `directory`: Directory path to search within.
- `pattern`: Glob pattern to match filenames (e.g., `*.pdf`, `report-*.pdf`).

---

### `merge_pdfs_ordered`
**Description:** Finds and merges PDF files from a directory based on a specified order of filename patterns. Supports exact and fuzzy matching modes.

**Arguments:**
- `directory`: Directory path to search for PDF files.
- `order_patterns`: List of filename patterns defining the merge order.
- `output_path`: Full path where the merged PDF will be saved.
- `match_mode`: Matching mode (`exact` or `fuzzy`). Default is `exact`.

---

### `find_related_pdfs`
**Description:** Finds PDF files related to a target PDF by analyzing text content similarity using TF-IDF and cosine similarity.

**Arguments:**
- `target_pdf`: Full path to the reference PDF.
- `search_directory`: Directory path to search for related PDFs.
- `top_n`: Maximum number of related PDFs to return (default: 5).