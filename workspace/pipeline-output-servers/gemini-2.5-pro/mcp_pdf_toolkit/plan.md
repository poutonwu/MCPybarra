<thought>
I have completed the research. The search results confirm that `pypdf` (a successor to `PyPDF2`) is a strong candidate for core PDF operations like merging and splitting. For text extraction, which is crucial for the `find-related-pdfs` tool, `pdfplumber` and other modern libraries are mentioned. For content similarity, I'll need a text analysis library. A simple approach would be to extract text using `pypdf` or `pdfplumber` and then use a library like `scikit-learn` to calculate TF-IDF vectors and cosine similarity. This combination seems robust enough to fulfill all the user's requirements.

Now I will proceed to generate the final implementation plan. I will structure it according to the mandated format.

**Deconstruction of the Request:**

1.  **`merge-pdfs`**:
    *   **Inputs**: A list of PDF file paths, an output file path.
    *   **Output**: A status message indicating success or failure.
    *   **Functionality**: Combine multiple PDF files into a single PDF.
2.  **`extract-pages`**:
    *   **Inputs**: A source PDF file path, a list/range of pages to extract, an output file path.
    *   **Output**: A status message.
    *   **Functionality**: Create a new PDF containing only the specified pages from the source PDF.
3.  **`search-pdfs`**:
    *   **Inputs**: A directory path, a filename pattern (glob or regex).
    *   **Output**: A list of matching file paths.
    *   **Functionality**: Search for PDF files in a directory that match a given pattern.
4.  **`merge-pdfs-ordered`**:
    *   **Inputs**: A directory path, a list of filename patterns defining the order, an output file path, a matching mode (exact/fuzzy).
    *   **Output**: A status message.
    *   **Functionality**: Find PDFs in a directory based on a list of patterns and merge them in that specific order. Fuzzy matching will likely involve finding the best match for each pattern.
5.  **`find-related-pdfs`**:
    *   **Inputs**: A target PDF file path, a directory path to search within.
    *   **Output**: A list of related PDF file paths, possibly with a similarity score.
    *   **Functionality**: Analyze the content of the target PDF (extract text) and compare it against the content of other PDFs in the directory to find semantically similar documents. Filename patterns could be a secondary factor.

**Library Selection:**

*   **Core PDF Operations (`merge`, `extract`):** `pypdf` is the modern and maintained choice.
*   **File Searching (`search`, `ordered-merge`):** Python's built-in `os` and `glob` modules are sufficient. For fuzzy filename matching, `thefuzz` (formerly `fuzzywuzzy`) is a good option.
*   **Text Extraction (`find-related`):** `pypdf` has text extraction capabilities.
*   **Content Analysis (`find-related`):** `scikit-learn` for TF-IDF vectorization and cosine similarity calculation.

Now, I will construct the final plan document.# MCP Tools Plan

### Tool 1: `merge_pdfs`

*   **Function Name**: `merge_pdfs`
*   **Description**: 将多个指定的PDF文件合并成一个单独的PDF文件。
*   **Parameters**:
    *   `pdf_paths` (`list[str]`): 一个包含要合并的PDF文件完整路径的列表。
    *   `output_path` (`str`): 合并后生成的PDF文件的保存路径。
*   **Return Value**: `dict`: 返回一个包含操作状态和消息的字典。例如: `{"status": "success", "message": "Files merged successfully into output.pdf"}`。

### Tool 2: `extract_pages`

*   **Function Name**: `extract_pages`
*   **Description**: 从一个PDF文件中提取指定的页面，并创建一个新的PDF文件。
*   **Parameters**:
    *   `source_path` (`str`): 源PDF文件的完整路径。
    *   `pages` (`list[int]`): 一个包含要提取的页码的列表 (页码从0开始)。
    *   `output_path` (`str`): 提取页面后生成的新PDF文件的保存路径。
*   **Return Value**: `dict`: 返回一个包含操作状态和消息的字典。例如: `{"status": "success", "message": "Extracted 3 pages into new_file.pdf"}`。

### Tool 3: `search_pdfs`

*   **Function Name**: `search_pdfs`
*   **Description**: 在指定目录中根据glob模式搜索匹配的PDF文件。
*   **Parameters**:
    *   `directory` (`str`): 要搜索的目录路径。
    *   `pattern` (`str`): 用于匹配文件名的glob模式 (例如, `'*.pdf'`, `'report-*.pdf'`)。
*   **Return Value**: `list[str]`: 返回一个包含所有匹配的PDF文件完整路径的列表。

### Tool 4: `merge_pdfs_ordered`

*   **Function Name**: `merge_pdfs_ordered`
*   **Description**: 在指定目录中根据文件名模式列表，按指定顺序查找并合并PDF文件。支持精确和模糊匹配模式。
*   **Parameters**:
    *   `directory` (`str`): 要搜索PDF文件的目录路径。
    *   `order_patterns` (`list[str]`): 一个定义合并顺序的文件名模式列表。
    *   `output_path` (`str`): 合并后生成的PDF文件的保存路径。
    *   `match_mode` (`str`): 匹配模式，可选值为 `'exact'` 或 `'fuzzy'`。默认为 `'exact'`。
*   **Return Value**: `dict`: 返回一个包含操作状态、消息以及实际合并文件列表的字典。例如: `{"status": "success", "message": "Files merged in specified order.", "merged_files": ["path/to/report-1.pdf", "path/to/summary.pdf"]}`。

### Tool 5: `find_related_pdfs`

*   **Function Name**: `find_related_pdfs`
*   **Description**: 根据一个目标PDF文件的内容，在指定目录中分析并查找内容相关或文件名模式相似的PDF文件。
*   **Parameters**:
    *   `target_pdf` (`str`): 作为分析基准的目标PDF文件的完整路径。
    *   `search_directory` (`str`): 要在其中搜索相关文件的目录路径。
    *   `top_n` (`int`): 返回最相关的PDF文件数量，默认为5。
*   **Return Value**: `list[dict]`: 返回一个相关PDF文件列表，每个元素是一个包含文件路径和相似度得分的字典。例如: `[{"file_path": "path/to/related_doc.pdf", "similarity_score": 0.85}, ...]`。

# Server Overview

该MCP服务器旨在提供一个自动化的PDF文件处理服务。它封装了核心的PDF操作功能，包括合并多个PDF文件、从文件中提取特定页面、按模式搜索文件、按指定顺序合并文件，以及基于内容分析查找相关PDF文档。所有功能都将通过清晰定义的MCP工具接口暴露，以便语言模型或其他客户端可以调用。

# File to be Generated

*   `mcp_pdf_server.py`

# Dependencies

*   `mcp`
*   `pypdf`
*   `scikit-learn`
*   `thefuzz`