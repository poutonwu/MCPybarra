# mcp_text_file_processor

## Overview

The `mcp_text_file_processor` is a Model Context Protocol (MCP) server that provides a set of tools for reading, writing, and manipulating text files. It allows clients to perform operations such as creating, reading, appending to, modifying, and patching the contents of text files with concurrency control via file hashing.

This server is ideal for integrating file manipulation capabilities into LLM workflows while ensuring robustness, transparency, and safety through proper error handling and hash-based version control.

---

## Installation

Before running the server, ensure you have Python 3.10 or higher installed.

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

If you don't already have a `requirements.txt`, make sure it includes:

```
mcp[cli]
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_text_file_processor.py
```

This will launch the MCP server using the standard I/O transport protocol.

---

## Available Tools

Below is a list of available tools provided by this MCP server:

### `get_text_file_contents`

**Description:** Reads the contents of one or more text files, optionally within a specified line range. Returns the lines and a SHA-256 hash of the file for concurrency control.

**Parameters:**
- `file_paths`: List of paths to the text files.
- `start_line`: Optional starting line number (0-based).
- `end_line`: Optional ending line number (exclusive).

**Returns:** A dictionary mapping each file path to an object containing:
- `lines`: List of lines read from the file.
- `hash`: SHA-256 hash of the file.

---

### `create_text_file`

**Description:** Creates a new text file at the specified path and writes initial content to it. Automatically creates any necessary parent directories.

**Parameters:**
- `file_path`: Path where the new file will be created.
- `content`: Initial content to write into the file.

**Returns:** A success message or error description.

---

### `append_text_file_contents`

**Description:** Appends additional content to an existing text file.

**Parameters:**
- `file_path`: Path to the target text file.
- `content`: Content to append to the file.

**Returns:** A success message or error description.

---

### `delete_text_file_contents`

**Description:** Deletes a specific range of lines from a text file.

**Parameters:**
- `file_path`: Path to the text file.
- `start_line`: Starting line number (inclusive, 0-based).
- `end_line`: Ending line number (exclusive).

**Returns:** A success message or error description.

---

### `insert_text_file_contents`

**Description:** Inserts content at a specific line in a text file.

**Parameters:**
- `file_path`: Path to the text file.
- `content`: Content to insert.
- `position`: Line number before which to insert (0-based).

**Returns:** A success message or error description.

---

### `patch_text_file_contents`

**Description:** Applies precise line replacements to a text file after verifying the current file hash to prevent conflicts.

**Parameters:**
- `file_path`: Path to the text file.
- `content_patches`: List of dictionaries with keys:
  - `position`: Line number to replace.
  - `new_content`: New content to place at that position.
- `expected_hash`: The expected SHA-256 hash of the file before applying changes.

**Returns:** A success message if the hash matches and patches are applied, or an error message if the hash mismatched or invalid input was provided.