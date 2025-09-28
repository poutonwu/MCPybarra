# mcp_word_document_processor

## Overview

The `mcp_word_document_processor` is a Model Context Protocol (MCP) server that provides a set of tools for creating, modifying, and interacting with Microsoft Word (.docx) documents. This server enables external models and tools to perform common document manipulation tasks such as adding text, headings, styles, footnotes, and applying password protection.

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10 or later installed.
2. Install the MCP SDK and required libraries:

```bash
pip install mcp[cli] python-docx pywin32
```

3. If using a `requirements.txt` file, install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the Server

To run the server, execute the Python script from the command line:

```bash
python mcp_word_document_processor.py
```

This starts the MCP server using the default `stdio` transport. You can modify the `mcp.run()` call in the script to use `sse` or `http` if needed.

## Available Tools

Below is a list of available tools exposed via the MCP interface:

### `create_document_tool`
Creates a new Word document and sets metadata such as title, author, and subject.

### `get_document_text_tool`
Extracts and returns all text content from a specified Word document.

### `add_paragraph_tool`
Adds a new paragraph with the specified text to the end of a document.

### `add_heading_tool`
Adds a heading with the specified text and level (1–9) to the document.

### `create_custom_style_tool`
Creates a custom paragraph style with specified font size, bold, and italic formatting.

### `format_text_tool`
Applies a specified style to a range of text defined by start and end positions.

### `protect_document_tool`
Protects a Word document with a password to restrict editing or opening.

### `add_footnote_to_document_tool`
Adds a footnote with the specified text to the document.

### `get_paragraph_text_from_document_tool`
Retrieves the text from a specific paragraph based on its index.

### `find_text_in_document_tool`
Searches for a given text string in the document and returns the indices of paragraphs where it is found.

### `remove_password_protection`
Removes password protection from a Word document.