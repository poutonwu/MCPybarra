# mcp_automated_pdf_tool

## Overview

The `mcp_automated_pdf_tool` is a Model Context Protocol (MCP) server that provides a suite of tools for automating PDF file operations. It allows users to merge, extract pages from, search for, and organize PDF files based on content or filename patterns.

This server is ideal for use cases involving batch processing of PDF documents, such as report generation, document organization, and content-based file discovery.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed.

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

If you don't already have a `requirements.txt`, it should include:

```
PyPDF2
fuzzywuzzy
textdistance
mcp[cli]
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_automated_pdf_tool.py
```

By default, the server uses standard input/output (`stdio`) transport. You can change the transport method by passing an argument to `mcp.run()` in the code (e.g., `"sse"` or `"http"`).

---

## Available Tools

Below are the available tools exposed via the MCP protocol:

### 1. `merge_pdfs`

**Description:** Merges multiple PDF files into a single PDF.

**Args:**
- `file_paths`: List of paths to the PDF files to be merged.
- `output_path`: Path where the merged PDF will be saved.

**Example:**
```python
merge_pdfs(["file1.pdf", "file2.pdf"], "merged_output.pdf")
```

---

### 2. `extract_pages`

**Description:** Extracts specific pages from a PDF and saves them as a new file.

**Args:**
- `file_path`: Path to the source PDF.
- `page_numbers`: List of page numbers to extract (starting from 1).
- `output_path`: Path where the extracted pages will be saved.

**Example:**
```python
extract_pages("input.pdf", [1, 3, 5], "pages_output.pdf")
```

---

### 3. `search_pdfs`

**Description:** Searches for PDF files matching a given pattern in a specified directory.

**Args:**
- `directory`: Directory to search in.
- `pattern`: Filename pattern (e.g., `"*.pdf"`).

**Returns:** A list of matching PDF file paths.

**Example:**
```python
search_pdfs("./documents", "*.pdf")
```

---

### 4. `merge_pdfs_ordered`

**Description:** Merges PDFs in a specific order, optionally using fuzzy matching for filenames.

**Args:**
- `file_paths`: List of all PDF files available for merging.
- `order`: List of patterns defining the desired merge order.
- `fuzzy_match`: Whether to use fuzzy matching for ordering (default: `False`).
- `output_path`: Path for the final merged output file.

**Example:**
```python
merge_pdfs_ordered(["report_part1.pdf", "report_part2.pdf"], ["part2", "part1"], True, "ordered_merged.pdf")
```

---

### 5. `find_related_pdfs`

**Description:** Finds PDF files related to a target PDF based on content similarity.

**Args:**
- `target_file`: Path to the reference PDF file.
- `directory`: Directory to search for related files.
- `similarity_threshold`: Minimum similarity score (0.0 to 1.0) to consider a match (default: `0.8`).

**Returns:** A list of file paths to PDFs with similar content.

**Example:**
```python
find_related_pdfs("annual_report.pdf", "./reports", 0.85)
```

---