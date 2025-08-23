# mcp_word_document_automation

## Overview

The `mcp_word_document_automation` server provides a set of tools for programmatically creating, editing, and managing Microsoft Word documents (`.docx`) using the Model Context Protocol (MCP). This allows large language models (LLMs) to interact with Word documents by adding content such as paragraphs, headings, tables, and page breaks, as well as performing document management tasks like saving and copying files.

## Installation

Before running the server, ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
python-docx
httpx
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_word_document_automation.py
```

This will launch the MCP server using standard input/output transport, allowing integration with compatible clients or LLMs.

## Available Tools

Below is a list of available tools provided by the server:

### 1. `create_document()`

Creates a new Word document named `new_document.docx`.

**Example:**
```python
create_document()
```

---

### 2. `open_document(file_path: str)`

Opens an existing Word document from the specified file path.

**Example:**
```python
open_document("example.docx")
```

---

### 3. `save_document()`

Saves the currently opened document as `saved_document.docx`.

**Example:**
```python
save_document()
```

---

### 4. `save_as_document(new_file_path: str)`

Saves the current document under a new file name or path.

**Example:**
```python
save_as_document("new_name.docx")
```

---

### 5. `create_document_copy(copy_file_path: str)`

Saves a copy of the current document at the specified file path.

**Example:**
```python
create_document_copy("copy_name.docx")
```

---

### 6. `add_paragraph(text: str)`

Adds a paragraph with the given text to the document.

**Example:**
```python
add_paragraph("This is a new paragraph.")
```

---

### 7. `add_heading(text: str, level: int)`

Adds a heading with the specified text and level (e.g., 1 for H1, 2 for H2).

**Example:**
```python
add_heading("Chapter 1", 1)
```

---

### 8. `add_table(rows: int, columns: int)`

Inserts a table with the specified number of rows and columns.

**Example:**
```python
add_table(3, 4)
```

---

### 9. `add_page_break()`

Inserts a manual page break into the document.

**Example:**
```python
add_page_break()
```

---