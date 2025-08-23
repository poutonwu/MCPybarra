# mcp_word_document_automation

This server provides a set of tools for automating the creation and manipulation of Microsoft Word (.docx) documents. It allows users to create, modify, format, and convert Word documents programmatically via the Model Context Protocol (MCP).

## Installation

Before running the server, ensure you have Python 3.10+ installed and then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure the `workspace` directory exists in your project folder or create it manually:

```bash
mkdir workspace
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_word_document_automation_server.py
```

## Available Tools

The following tools are available for use with this MCP server:

### 1. `create_document`
Creates a new Word document and sets metadata such as title, author, and keywords.

**Parameters:**
- `title`: The title of the document.
- `author`: Optional; defaults to "Unknown".
- `keywords`: Optional list of keywords.

---

### 2. `get_document_text`
Extracts the full text content of a specified Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.

---

### 3. `add_paragraph`
Adds a paragraph of text to a specified Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `text`: Text to add as a paragraph.

---

### 4. `add_heading`
Adds a heading at a specified level (1–9) to a Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `text`: Text of the heading.
- `level`: Heading level (must be between 1 and 9).

---

### 5. `create_custom_style`
Creates a custom paragraph style (font, size, color) for use in the document.

**Parameters:**
- `style_name`: Name of the custom style.
- `font`: Font name.
- `size`: Font size in points.
- `color`: Font color in HEX format (e.g., "#FF0000").

---

### 6. `format_text`
Applies formatting (bold, italic, underline) to a specific range of text in the document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `start_pos`: Start position of the text range.
- `end_pos`: End position of the text range.
- `format_options`: Dictionary specifying formatting options like bold, italic, underline.

---

### 7. `protect_document`
Sets password protection for a Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `password`: Password to protect the document.

> **Note:** Requires the `pywin32` package.

---

### 8. `add_footnote_to_document`
Adds a footnote to a specified Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `text`: Text of the footnote.

---

### 9. `get_paragraph_text_from_document`
Extracts the text of a specific paragraph from a document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `paragraph_index`: Index of the paragraph to retrieve.

---

### 10. `find_text_in_document`
Searches for a specific string within a document and returns its positions.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `search_text`: Text to search for.

---

### 11. `add_table`
Adds a table with specified dimensions and data to a Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `rows`: Number of rows.
- `cols`: Number of columns.
- `data`: List of lists containing the table data.

---

### 12. `add_image`
Inserts an image into a specified Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `image_path`: Path to the image file.

---

### 13. `add_page_break`
Adds a page break to a specified Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.

---

### 14. `add_header_footer`
Adds a header or footer to a specified Word document.

**Parameters:**
- `document_id`: Path or identifier of the document.
- `text`: Text to add to the header or footer.
- `is_header`: Boolean indicating whether to add a header (`True`) or footer (`False`).

---

### 15. `convert_to_pdf`
Converts a Word document to PDF format.

**Parameters:**
- `document_id`: Path or identifier of the document.

> **Note:** Requires the `pywin32` package.