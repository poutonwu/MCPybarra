# mcp_word_document_processor

## Overview

The `mcp_word_document_processor` is a Model Context Protocol (MCP) server that enables interaction with Microsoft Word documents via a set of tools. It allows users to create, open, edit, and manipulate `.docx` files programmatically using LLM-integrated workflows.

This server supports document creation, text editing, table manipulation, metadata retrieval, and more, making it ideal for automating document processing tasks.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, use the following command to install the necessary packages:

```bash
pip install python-docx mcp
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_word_document_processor.py
```

Ensure the script file is named appropriately (e.g., `mcp_word_document_processor.py`) or replace it with the actual filename.

## Available Tools

Below is a list of available tools provided by the server:

### Document Management
- **`create_document()`**  
  Creates a new Word document in memory.
- **`open_document(document_path: str)`**  
  Opens an existing `.docx` file from the specified path.
- **`save_document()`**  
  Saves the current document as `current_document.docx`.
- **`save_as_document(new_path: str)`**  
  Saves the current document to a new file path.
- **`create_document_copy(copy_path: str)`**  
  Saves a copy of the current document to the specified path.

### Content Editing
- **`add_paragraph(text: str)`**  
  Adds a new paragraph with the given text.
- **`add_heading(text: str, level: int = 1)`**  
  Adds a heading with the specified level (1–9).
- **`add_table(rows: int, columns: int)`**  
  Inserts a table with the specified number of rows and columns.
- **`add_page_break()`**  
  Inserts a page break at the current location.
- **`delete_paragraph(paragraph_index: int)`**  
  Deletes the paragraph at the specified index.
- **`delete_text(text: str)`**  
  Removes all occurrences of the specified text from the document.

### Search & Replace
- **`search_text(query: str)`**  
  Searches for the specified text and returns matching paragraphs and their indices.
- **`find_and_replace(find_text: str, replace_text: str)`**  
  Replaces all occurrences of `find_text` with `replace_text`.

### Table Manipulation
- **`add_table_row(table_index: int)`**  
  Adds a new row to the specified table.
- **`delete_table_row(table_index: int, row_index: int)`**  
  Deletes the specified row from the selected table.
- **`edit_table_cell(table_index: int, row_index: int, column_index: int, new_text: str)`**  
  Edits the content of a specific cell in a table.
- **`merge_table_cells(table_index: int, start_row: int, start_column: int, end_row: int, end_column: int)`**  
  Merges the specified range of cells in a table.

### Document Properties
- **`get_document_info()`**  
  Retrieves metadata such as author, creation time, modification time, and word count.

### Page Settings
- **`set_page_margins(left: float, right: float, top: float, bottom: float)`**  
  Sets the margins for all sections in the document (in inches).