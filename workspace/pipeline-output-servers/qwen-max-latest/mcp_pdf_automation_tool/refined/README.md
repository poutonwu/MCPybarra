# mcp_pdf_automation_tool

## Overview

`mcp_pdf_automation_tool` is a Model Context Protocol (MCP) server that provides a set of tools for automating common PDF manipulation tasks. These tools allow users to merge, extract, search, and organize PDF files programmatically through an MCP interface.

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the MCP SDK and required libraries:

```bash
pip install mcp[cli] PyPDF2 rapidfuzz
```

3. Save the server code as `mcp_pdf_automation_tool.py`.

## Running the Server

Run the server using the following command:

```bash
python mcp_pdf_automation_tool.py
```

This will start the MCP server using standard input/output transport.

## Available Tools

The server exposes the following tools via the MCP protocol:

### `merge_pdfs`
**Description:** Merges multiple PDF files into a single file.

**Args:**
- `pdf_files`: List of paths to the PDF files. Required.

**Returns:** Path to the merged PDF file.

**Example:**
```python
merge_pdfs(pdf_files=["file1.pdf", "file2.pdf"])
```

---

### `extract_pages`
**Description:** Extracts specific pages from a PDF file and saves them as a new file.

**Args:**
- `pdf_file`: Path to the source PDF file. Required.
- `pages`: List of page numbers to extract. Required.
- `output_path`: Path where the new PDF file will be saved. Required.

**Returns:** Path to the new PDF file containing the extracted pages.

**Example:**
```python
extract_pages(pdf_file="source.pdf", pages=[1, 3, 5], output_path="extracted_pages.pdf")
```

---

### `search_pdfs`
**Description:** Searches for PDF files matching a specific pattern in a given directory.

**Args:**
- `directory`: Directory path to search within. Required.
- `pattern`: Pattern to match PDF filenames. Required.

**Returns:** List of paths to the matching PDF files.

**Example:**
```python
search_pdfs(directory="/path/to/files", pattern="report*.pdf")
```

---

### `merge_pdfs_ordered`
**Description:** Merges PDF files following a specified order, supporting both exact and fuzzy matching.

**Args:**
- `pdf_files`: List of paths to the PDF files. Required.
- `order_pattern`: Pattern defining the merge order. Required.
- `fuzzy_match`: Whether to use fuzzy matching for ordering. Optional, default is False.

**Returns:** Path to the merged PDF file.

**Example:**
```python
merge_pdfs_ordered(pdf_files=["file1.pdf", "file2.pdf"], order_pattern="file?.pdf", fuzzy_match=True)
```

---

### `find_related_pdfs`
**Description:** Finds related PDF files based on the content and filename patterns of a target PDF file.

**Args:**
- `target_pdf`: Path to the target PDF file. Required.
- `content_similarity_threshold`: Threshold for content similarity. Optional, default is 0.8.

**Returns:** List of paths to related PDF files.

**Example:**
```python
find_related_pdfs(target_pdf="target_report.pdf", content_similarity_threshold=0.8)
```