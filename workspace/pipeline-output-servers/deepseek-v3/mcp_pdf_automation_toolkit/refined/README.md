# mcp_pdf_automation_toolkit

## Overview

The `mcp_pdf_automation_toolkit` is a Model Context Protocol (MCP) server that provides tools for automating PDF file operations. It allows users to merge PDFs, extract specific pages, search for PDFs by pattern, merge in a defined order (with optional fuzzy matching), and find related PDFs based on content similarity.

This server is ideal for integrating PDF automation capabilities into LLM-based applications using the MCP protocol.

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

### Requirements

Your `requirements.txt` should include:

```
mcp[cli]
PyPDF2
fuzzywuzzy
python-Levenshtein
scikit-learn
PyMuPDF
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_pdf_automation_toolkit.py
```

By default, the server communicates via standard input/output (stdio).

## Available Tools

Below is a list of available tools provided by the server:

### 1. `merge_pdfs`

**Description:** Merges multiple PDF files into a single PDF.

**Arguments:**
- `file_paths`: A list of paths to the PDF files to be merged.
- `output_path`: The path where the merged PDF will be saved.

**Returns:** A message indicating success or failure of the merge operation.

---

### 2. `extract_pages`

**Description:** Extracts specific pages from a source PDF and saves them as a new PDF.

**Arguments:**
- `source_path`: Path to the source PDF file.
- `pages`: A list of page numbers to extract (0-indexed).
- `output_path`: Path to save the extracted pages.

**Returns:** A message indicating success or failure of the extraction.

---

### 3. `search_pdfs`

**Description:** Searches a directory for PDF files matching a given filename pattern.

**Arguments:**
- `directory`: Directory path to search within.
- `pattern`: Filename pattern to match (e.g., `*.pdf`, `report_*.pdf`).

**Returns:** A list of matching PDF file paths.

---

### 4. `merge_pdfs_ordered`

**Description:** Merges PDF files in a specified order, with optional fuzzy matching for filenames.

**Arguments:**
- `file_paths`: List of available PDF file paths.
- `order`: List of filenames or partial names in the desired merge order.
- `output_path`: Path to save the merged PDF.
- `fuzzy_match`: If `True`, uses fuzzy matching to find best-fit files for each entry in the order.

**Returns:** A message indicating success or failure of the ordered merge.

---

### 5. `find_related_pdfs`

**Description:** Finds PDFs related to a target PDF based on content similarity.

**Arguments:**
- `target_path`: Path to the target PDF to compare against.
- `directory`: Directory to search for related PDFs.
- `content_similarity_threshold`: Minimum cosine similarity threshold (default: 0.7).

**Returns:** A list of file paths to PDFs that are content-wise similar to the target.