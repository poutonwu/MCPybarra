# mcp_word_document_automation

A server that provides Microsoft Word document automation capabilities via the Model Context Protocol (MCP). This server enables seamless integration between large language models and document processing tasks.

## Overview

The `mcp_word_document_automation` server allows LLMs to create, edit, manipulate, and manage Microsoft Word (.docx) documents programmatically. It supports a wide range of operations including creating documents, adding content, modifying tables, searching and replacing text, setting page margins, and more.

This server is built using the `python-docx` library and implements the MCP protocol to expose its functionality to LLMs through tools.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
python-docx
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_word_document_automation.py
```

Make sure the Python file is executable and that all dependencies are properly installed.

## Available Tools

Here is a list of available MCP tools provided by this server:

### Document Management
- **create_document()**: Creates a new Word document.
- **open_document(file_path: str)**: Opens an existing Word document from the specified file path.
- **save_document()**: Saves the current document with its original filename.
- **save_as_document(file_path: str)**: Saves the current document to a new file path or name.
- **create_document_copy(file_path: str)**: Creates a copy of the current document at the specified location.

### Content Manipulation
- **add_paragraph(text: str)**: Adds a paragraph with the specified text to the document.
- **add_heading(text: str, level: int)**: Adds a heading with the specified text and level (1–9).
- **add_page_break()**: Inserts a page break into the document.

### Table Operations
- **add_table(rows: int, cols: int)**: Adds a table with the specified number of rows and columns.
- **add_table_row(table_index: int)**: Adds a row to the specified table.
- **delete_table_row(table_index: int, row_index: int)**: Deletes a specific row from a specified table.
- **edit_table_cell(table_index: int, row_index: int, col_index: int, new_content: str)**: Edits the content of a specific cell in a table.
- **merge_table_cells(table_index: int, start_row: int, end_row: int, start_col: int, end_col: int)**: Merges a range of cells in a specified table.
- **split_table(table_index: int, row_index: int)**: Splits a table into two at the specified row.

### Text Search & Replace
- **search_text(search_string: str)**: Searches for specific text within the document and returns paragraph indices where found.
- **find_and_replace(find_string: str, replace_string: str)**: Finds and replaces all instances of the specified text.
- **delete_paragraph(paragraph_index: int)**: Deletes the specified paragraph.
- **delete_text(text: str)**: Deletes all occurrences of the specified text from the document.

### Document Information
- **get_document_info()**: Retrieves metadata about the current document such as author, title, creation date, etc.

### Section Editing
- **replace_section(heading: str, new_content: str)**: Replaces the content of a section based on its heading.
- **edit_section_by_keyword(keyword: str, new_content: str)**: Edits a section based on a keyword match in the content.

### Page Layout
- **set_page_margins(top: float, right: float, bottom: float, left: float)**: Sets the page margins for the document in inches.