# mcp_word_document_processor

A Model Context Protocol (MCP) server that provides tools for creating, modifying, and extracting content from Microsoft Word (.docx) documents.

## Overview

The `mcp_word_document_processor` server enables seamless integration between large language models (LLMs) and document manipulation tasks using the `python-docx` library. It supports operations such as creating new documents with metadata, adding paragraphs and headings, defining custom styles, searching text, retrieving paragraph content, and more.

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your environment is using **Python 3.10 or higher**.

## Running the Server

To start the server using the standard input/output transport, run:

```bash
python mcp_word_document_processor.py
```

## Available Tools

Each tool is registered via the `@mcp.tool()` decorator and can be used by an MCP client to interact with Word documents.

### 1. `create_document`
Creates a new Word document and sets metadata (title, author, subject).

**Example:**
```python
create_document(title="Report", author="Alice", subject="Annual Review")
```

---

### 2. `get_document_text`
Extracts all text content from an existing document.

**Example:**
```python
get_document_text(file_path="Report.docx")
```

---

### 3. `add_paragraph`
Adds a new paragraph of text to the document.

**Example:**
```python
add_paragraph(file_path="Report.docx", text="This is a new paragraph.")
```

---

### 4. `add_heading`
Adds a heading of a specified level (1–6) to the document.

**Example:**
```python
add_heading(file_path="Report.docx", text="Introduction", level=2)
```

---

### 5. `create_custom_style`
Defines a custom paragraph style with font settings like name, size, bold, and italic.

**Example:**
```python
create_custom_style(file_path="Report.docx", style_name="CustomStyle", font_name="Arial", font_size=12, bold=True, italic=False)
```

---

### 6. `format_text`
Applies a custom style to a range of paragraphs in the document.

**Example:**
```python
format_text(file_path="Report.docx", start=0, end=2, style_name="CustomStyle")
```

---

### 7. `protect_document`
Attempts to password-protect the document (**currently not implemented** due to limitations in `python-docx`).

**Example:**
```python
protect_document(file_path="Report.docx", password="secret123")
```

---

### 8. `add_footnote_to_document`
Attempts to add a footnote to the document (**not implemented** in current version).

**Example:**
```python
add_footnote_to_document(file_path="Report.docx", text="Confidential information.")
```

---

### 9. `get_paragraph_text_from_document`
Retrieves the text of a specific paragraph by index.

**Example:**
```python
get_paragraph_text_from_document(file_path="Report.docx", paragraph_index=1)
```

---

### 10. `find_text_in_document`
Searches for occurrences of a given text string within the document.

**Example:**
```python
find_text_in_document(file_path="Report.docx", search_text="important")
```