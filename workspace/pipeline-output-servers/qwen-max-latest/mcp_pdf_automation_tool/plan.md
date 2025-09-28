### MCP Tools Plan

#### Tool 1: `merge_pdfs`
- **Description**: Merges multiple PDF files into a single file.
- **Parameters**:
  - `pdf_files`: List of paths to the PDF files (List[str]). Required.
- **Return Value**: Path to the merged PDF file (str).

#### Tool 2: `extract_pages`
- **Description**: Extracts specific pages from a PDF file and saves them as a new file.
- **Parameters**:
  - `pdf_file`: Path to the source PDF file (str). Required.
  - `pages`: List of page numbers to extract (List[int]). Required.
  - `output_path`: Path where the new PDF file will be saved (str). Required.
- **Return Value**: Path to the new PDF file containing the extracted pages (str).

#### Tool 3: `search_pdfs`
- **Description**: Searches for PDF files matching a specific pattern in a given directory.
- **Parameters**:
  - `directory`: Directory path to search within (str). Required.
  - `pattern`: Pattern to match PDF filenames (str). Required.
- **Return Value**: List of paths to the matching PDF files (List[str]).

#### Tool 4: `merge_pdfs_ordered`
- **Description**: Merges PDF files following a specified order, supporting both exact and fuzzy matching.
- **Parameters**:
  - `pdf_files`: List of paths to the PDF files (List[str]). Required.
  - `order_pattern`: Pattern defining the merge order (str). Required.
  - `fuzzy_match`: Whether to use fuzzy matching for ordering (bool). Optional, default is False.
- **Return Value**: Path to the merged PDF file (str).

#### Tool 5: `find_related_pdfs`
- **Description**: Finds related PDF files based on the content and filename patterns of a target PDF file.
- **Parameters**:
  - `target_pdf`: Path to the target PDF file (str). Required.
  - `content_similarity_threshold`: Threshold for content similarity (float). Optional, default is 0.8.
- **Return Value**: List of paths to related PDF files (List[str]).

### Server Overview
The server aims to automate PDF file processing with functionalities including merging PDFs, extracting specific pages, searching for PDFs by pattern, ordered merging of PDFs, and finding related PDFs based on content and filename patterns.

### File to be Generated
- **Filename**: `mcp_pdf_server.py`

### Dependencies
- `PyPDF2` or `pypdf`: For handling PDF operations such as merging and extracting pages.
- `fuzzywuzzy` or `rapidfuzz`: For implementing fuzzy matching when ordering PDFs for merging.
- `os`: For directory and file path manipulations.
- `re`: For pattern matching in filenames.