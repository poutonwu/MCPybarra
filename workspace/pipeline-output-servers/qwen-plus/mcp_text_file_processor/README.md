# mcp_text_file_processor

## Overview

`mcp_text_file_processor` is an MCP (Model Context Protocol) server that provides a set of tools for reading, writing, and modifying text files. It allows language models to interact with the file system in a secure and controlled manner, supporting operations such as reading file contents, creating new files, appending, inserting, deleting, and patching content within files.

This server ensures concurrency safety using SHA-256 hash validation and prevents path traversal attacks through strict file path validation.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following:

```
mcp[cli]
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_text_file_processor.py
```

By default, the server communicates via standard input/output (stdio). You can customize the transport method by passing it to `mcp.run()` if supported.

## Available Tools

The server provides the following MCP tools:

### `get_text_file_contents`

Reads content from one or more text files, optionally limited to a range of lines. Returns both the content and SHA-256 hashes of the files for concurrency control.

**Example:**
```python
get_text_file_contents(file_paths=["example.txt"], start_line=0, end_line=5)
```

---

### `create_text_file`

Creates a new text file and writes initial content into it.

**Example:**
```python
create_text_file(file_path="new_file.txt", content="This is the content")
```

---

### `append_text_file_contents`

Appends content to an existing text file.

**Example:**
```python
append_text_file_contents(file_path="existing_file.txt", content="\nNew appended content")
```

---

### `delete_text_file_contents`

Deletes a range of lines from a text file after validating the current SHA-256 hash to ensure consistency in concurrent environments.

**Example:**
```python
delete_text_file_contents(file_path="example.txt", start_line=2, end_line=5)
```

---

### `insert_text_file_contents`

Inserts content at a specific position in a text file after validating the current SHA-256 hash to ensure consistency in concurrent environments.

**Example:**
```python
insert_text_file_contents(file_path="example.txt", insert_line=3, content="Inserted content\n")
```

---

### `patch_text_file_contents`

Replaces the content of a specific line in a text file after verifying both the current content and the file's SHA-256 hash for concurrency safety.

**Example:**
```python
patch_text_file_contents(file_path="example.txt", line_number=4, old_content="Old content", new_content="New content")
```