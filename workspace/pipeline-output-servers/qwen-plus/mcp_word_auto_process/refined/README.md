# mcp_word_auto_process

## Overview
`mcp_word_auto_process` is a Model Context Protocol (MCP) server that provides an API for programmatic creation and manipulation of Microsoft Word (.docx) documents. It supports document creation, text formatting, adding paragraphs and headings, inserting images and tables, document protection, and conversion to PDF.

This server enables integration with LLMs to automate complex Word document operations through structured function calls.

## Installation
1. Ensure Python 3.10+ is installed.
2. Install the MCP SDK:
   ```bash
   pip install mcp[cli]
   ```
3. Install required dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

The following packages will be installed:
- python-docx: For creating and manipulating .docx files
- docx2pdf: For converting Word documents to PDF format
- fastmcp: FastMCP implementation for the MCP protocol

## Running the Server
To start the server, run the Python script from the command line:
```bash
python mcp_word_auto_process_server.py
```

By default, the server uses standard input/output (stdio) transport. You can specify other transports like "sse" or "http" if supported in the implementation.

## Available Tools

### Document Management
- **`create_document`**  
  Creates a new Word document with optional metadata (author, title, subject, keywords)

- **`get_document_text`**  
  Extracts all text content from a specified document

### Paragraph Operations
- **`add_paragraph`**  
  Adds a new paragraph to a document

- **`add_heading`**  
  Adds a heading with specified level (1-9) to a document

- **`get_paragraph_text_from_document`**  
  Retrieves text content from a specific paragraph

- **`format_text`**  
  Applies formatting (bold, italic, font size, font name) to a portion of text in a paragraph

- **`find_text_in_document`**  
  Searches for text within a document and returns matching paragraph IDs and positions

### Content Insertion
- **`add_table`**  
  Inserts a table with specified dimensions and data into a document

- **`add_image`**  
  Inserts an image from a file path with specified dimensions

- **`add_page_break`**  
  Inserts a page break at the current position

- **`add_header_footer`**  
  Sets custom header and/or footer text for the document

- **`convert_to_pdf`**  
  Converts the Word document to PDF format and saves it to a specified path

### Advanced Features
- **`create_custom_style`**  
  Creates a custom style in the document for consistent formatting

- **`protect_document`**  
  Placeholder for document protection functionality (requires additional libraries)

- **`add_footnote_to_document`**  
  Placeholder for adding footnotes (python-docx does not currently support this natively)