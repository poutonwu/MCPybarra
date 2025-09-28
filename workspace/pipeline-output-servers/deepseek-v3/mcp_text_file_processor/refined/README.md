# mcp_text_file_processor

## Overview

`mcp_text_file_processor` is an MCP (Model Context Protocol) server that provides a set of tools for reading, writing, and modifying text files. It enables seamless integration between large language models (LLMs) and file system operations, supporting concurrency control via SHA-256 hashing.

This server allows for:
- Reading file contents with optional line range
- Creating new text files
- Appending content to existing files
- Deleting specific lines from files
- Inserting content at specified line numbers
- Applying multiple modifications safely using hash validation

## Installation

To install dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
```

## Running the Server

To run the server, execute the Python script from the command line:

```bash
python mcp_text_file_processor.py
```

By default, the server uses the `stdio` transport protocol.

## Available Tools

### `get_text_file_contents`

Reads the contents of one or more text files, optionally within a specified line range. Returns both the content and a SHA-256 hash for concurrency control.

**Arguments:**
- `file_paths`: List of file paths to read.
- `line_range`: Optional tuple `(start_line, end_line)` indicating which lines to read.

---

### `create_text_file`

Creates a new text file with the given content.

**Arguments:**
- `file_path`: Path where the new file will be created.
- `content`: The content to write into the new file.

---

### `append_text_file_contents`

Appends content to an existing text file.

**Arguments:**
- `file_path`: Path to the file to append to.
- `content`: The content to append.

---

### `delete_text_file_contents`

Deletes a specific range of lines from a text file.

**Arguments:**
- `file_path`: Path to the file.
- `line_range`: Tuple `(start_line, end_line)` indicating which lines to delete.

---

### `insert_text_file_contents`

Inserts content into a text file at a specific line number.

**Arguments:**
- `file_path`: Path to the file.
- `line_number`: Line number where the content will be inserted.
- `content`: Content to insert.

---

### `patch_text_file_contents`

Applies a list of precise modifications (insert, delete, replace) to a text file after validating the current file hash to avoid conflicts.

**Arguments:**
- `file_path`: Path to the file.
- `modifications`: List of modification dictionaries, each specifying:
  - `action`: One of `"insert"`, `"delete"`, or `"replace"`.
  - `line_number`: Target line number for the action.
  - `content`: Content to insert or replace (for applicable actions).
- `expected_hash`: Expected SHA-256 hash of the file before applying changes.

Returns the result along with the new hash after modifications.