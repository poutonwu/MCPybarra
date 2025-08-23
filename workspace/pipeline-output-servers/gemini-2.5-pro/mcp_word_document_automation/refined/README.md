# mcp_word_document_automation

A Model Context Protocol (MCP) server that provides tools for automating Microsoft Word document creation and manipulation.

## Overview

This server enables integration with external LLMs to programmatically create, modify, and extract content from `.docx` files. It supports a wide range of operations including creating documents, adding paragraphs and headings, formatting text, inserting images, tables, page breaks, headers/footers, and converting documents to PDF.

---

## Installation

1. Ensure Python 3.10 or higher is installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:
```
python-docx
pdf2docx
mcp[cli]
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_word_document_automation.py
```

Replace `mcp_word_document_automation.py` with the actual name of your server script.

---

## Available Tools

Below is a list of available MCP tools and their functionality:

### Document Creation & Metadata
- **`create_document(file_path, title, author, subject, keywords)`**  
  Creates a new `.docx` file and sets metadata like title, author, subject, and keywords.

- **`protect_document(file_path, password)`**  
  *Not supported* — Attempts to set write protection on a document (currently not supported by `python-docx`).

### Content Extraction
- **`get_document_text(file_path)`**  
  Returns all text content from a document, with paragraphs separated by newlines.

- **`get_paragraph_text_from_document(file_path, paragraph_index)`**  
  Retrieves the text of a specific paragraph based on its index.

- **`find_text_in_document(file_path, search_text)`**  
  Searches for a given string and returns the indices of paragraphs containing it.

### Text Manipulation
- **`add_paragraph(file_path, text)`**  
  Adds a new paragraph to the end of the document.

- **`add_heading(file_path, text, level)`**  
  Adds a heading at the specified level (0–9) to the document.

- **`format_text(file_path, search_text, bold, italic)`**  
  Applies bold and/or italic formatting to the first occurrence of a given text string.

### Styling
- **`create_custom_style(file_path, style_name, font_name, font_size_pt, bold, italic)`**  
  Creates a custom paragraph style with specified font properties.

### Insertions
- **`add_table(file_path, rows, cols)`**  
  Inserts a table with the specified number of rows and columns.

- **`add_image(doc_file_path, image_file_path, width_inches)`**  
  Adds an image to the document from a local file path, optionally setting its width in inches.

- **`add_page_break(file_path)`**  
  Inserts a page break at the end of the document.

- **`add_footer(file_path, footer_text)`**  
  Sets or replaces the footer text for the main section of the document.

- **`add_header(file_path, header_text)`**  
  Sets or replaces the header text for the main section of the document.

- **`add_footnote_to_document(file_path, paragraph_index, footnote_text)`**  
  *Not supported* — Attempts to add a footnote (not directly supported by `python-docx`).

### Conversion
- **`convert_to_pdf(docx_path, pdf_path)`**  
  Converts a `.docx` file into a `.pdf` using the `pdf2docx` library.

--- 

For more detailed usage examples and parameter descriptions, refer to the function docstrings in the code.