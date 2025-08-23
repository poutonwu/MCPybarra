# mcp_word_document_automation

A Model Context Protocol (MCP) server that provides tools for automating Microsoft Word document creation and manipulation.

---

## Overview

The `mcp_word_document_automation` server enables seamless integration between large language models (LLMs) and Python-based Word document automation using the `python-docx` library. It allows LLMs to create, open, edit, and manage Word documents programmatically through a set of well-defined tools.

This server supports operations such as adding paragraphs and headings, inserting tables, searching and replacing text, modifying document structure, and adjusting layout settings like page margins.

---

## Installation

Before running the server, ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
python-docx
```

---

## Running the Server

To start the server, run the following command in your terminal:

```bash
python mcp_word_document_automation.py
```

Make sure the script file is named accordingly (e.g., `mcp_word_document_automation.py`).

---

## Available Tools

Below is a list of available MCP tools with brief descriptions based on their functionality:

### Document Management
- **`create_document(file_name: str)`**  
  Creates a new Word document with the specified file name.
- **`open_document(file_path: str)`**  
  Opens an existing Word document from the given file path.
- **`save_document(file_path: str)`**  
  Saves the currently open document to the specified file path.
- **`save_as_document(new_file_path: str)`**  
  Saves the current document with a new name or at a new location.
- **`create_document_copy(copy_file_path: str)`**  
  Creates a copy of the currently open document at the specified file path.

### Content Editing
- **`add_paragraph(text: str)`**  
  Adds a new paragraph with the specified text to the document.
- **`add_heading(text: str, level: int)`**  
  Adds a heading with the specified text and level (1–9).
- **`delete_paragraph(paragraph_index: int)`**  
  Deletes the paragraph at the specified index.
- **`delete_text(text_to_delete: str)`**  
  Removes all occurrences of the specified text from the document.
- **`find_and_replace(old_text: str, new_text: str)`**  
  Replaces all instances of `old_text` with `new_text` in the document.
- **`search_text(query: str)`**  
  Searches for the specified text and returns a list of locations where it was found.

### Table Manipulation
- **`add_table(rows: int, cols: int)`**  
  Inserts a new table with the specified number of rows and columns.
- **`add_table_row(table_index: int)`**  
  Adds a new row to the table at the specified index.
- **`delete_table_row(table_index: int, row_index: int)`**  
  Deletes the specified row from the table at the given index.
- **`edit_table_cell(table_index: int, row_index: int, col_index: int, new_content: str)`**  
  Edits the content of a specific cell in a table.
- **`merge_table_cells(table_index: int, start_row: int, start_col: int, end_row: int, end_col: int)`**  
  Merges cells within a table from the starting to the ending coordinates.
- **`split_table(table_index: int, split_row_index: int)`**  
  Splits a table into two at the specified row.

### Layout and Structure
- **`add_page_break()`**  
  Inserts a page break at the current cursor position.
- **`set_page_margins(top: float, bottom: float, left: float, right: float)`**  
  Sets the page margins for the entire document in inches.

### Document Information
- **`get_document_info()`**  
  Retrieves metadata about the current document, including the number of paragraphs and tables.

### Section Management
- **`replace_section(section_title: str, new_content: str)`**  
  Replaces the content of a section identified by its title.
- **`edit_section_by_keyword(keyword: str, new_content: str)`**  
  Edits a section based on a keyword match in the content.