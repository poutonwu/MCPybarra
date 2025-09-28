# mcp_word_document_processor

## Overview
The `mcp_word_document_processor` is a Model Context Protocol (MCP) server that provides a set of tools for creating, modifying, and converting Microsoft Word documents (.docx). It enables integration with LLMs to automate tasks such as document creation, text formatting, metadata management, and conversion to PDF.

This server uses the `python-docx` library for working with Word files and `docx2pdf` for exporting them to PDF format. The tools are designed to be robust, secure, and easy to use in both development and production environments.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies using:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install the necessary packages manually:

```bash
pip install mcp[cli] python-docx docx2pdf
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_word_document_processor.py
```

By default, the server communicates via standard input/output (stdio), which is suitable for local testing and integration with LLM platforms that support MCP.

---

## Available Tools

Below is a list of available tools exposed via the MCP protocol. Each tool corresponds to a function decorated with `@mcp.tool()` in the code.

| Tool Name | Description |
|-----------|-------------|
| **create_document** | Creates a new Word document with optional metadata (author, title, subject, keywords). |
| **get_document_text** | Extracts and returns all text content from an existing document. |
| **add_paragraph** | Adds a new paragraph of text to the end of a document. |
| **add_heading** | Adds a heading at a specified level to the document. |
| **create_custom_style** | Defines a new custom paragraph style with font settings (name, size, bold, italic, underline). |
| **format_text** | Applies formatting (bold, italic, underline) to all instances of specified text within the document. |
| **protect_document** | Placeholder for password protection (not supported by current library). |
| **add_footnote_to_document** | Adds a footnote to the last paragraph in the document. |
| **get_paragraph_text_from_document** | Retrieves the text of a specific paragraph by index. |
| **find_text_in_document** | Searches for paragraphs containing a specified text string. |
| **add_table** | Inserts a table with a specified number of rows and columns. |
| **add_picture** | Adds an image from a file path to the document, optionally setting its width. |
| **add_page_break** | Inserts a manual page break at the end of the document. |
| **add_header** | Sets or updates the primary header of the document. |
| **add_footer** | Sets or updates the primary footer of the document. |
| **convert_to_pdf** | Converts the Word document to PDF format, saving it with a `.pdf` extension. |

Each tool includes detailed documentation in its function docstring, including parameters, return values, and usage examples.