# mcp_text_file_manager

## Overview

The `mcp_text_file_manager` is a Model Context Protocol (MCP) server that provides tools for managing and manipulating text files. It allows reading, writing, modifying, and patching text files with concurrency control via file hashing.

This server supports resolving special path placeholders like `$temp_dir` and `$cwd`, ensuring seamless integration across different environments.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:

```
mcp[cli]
```

---

## Running the Server

To start the server, run the following command:

```bash
python mcp_text_file_manager.py
```

Ensure the script file (`mcp_text_file_manager.py`) contains the provided server code.

---

## Available Tools

Below is a list of available MCP tools exposed by this server:

### `get_text_file_contents(file_path: str, start_line: int = None, end_line: int = None) -> str`

Reads the content of a text file, optionally within a specified line range. Returns both the content and the SHA256 hash of the file to support concurrency control.

- **Example:**  
  ```python
  get_text_file_contents("example.txt", start_line=1, end_line=5)
  ```

---

### `create_text_file(file_path: str, content: str) -> str`

Creates a new text file at the specified path and writes the given content into it.

- **Example:**  
  ```python
  create_text_file("new_file.txt", "Hello, World!")
  ```

---

### `append_text_file_contents(file_path: str, content: str) -> str`

Appends the provided content to an existing text file.

- **Example:**  
  ```python
  append_text_file_contents("example.txt", "Additional text.")
  ```

---

### `delete_text_file_contents(file_path: str, start_line: int, end_line: int) -> str`

Deletes content in the specified line range from a text file.

- **Example:**  
  ```python
  delete_text_file_contents("example.txt", start_line=2, end_line=4)
  ```

---

### `insert_text_file_contents(file_path: str, line_number: int, content: str) -> str`

Inserts content at a specific position in a text file.

- **Example:**  
  ```python
  insert_text_file_contents("example.txt", line_number=3, content="Inserted text.")
  ```

---

### `patch_text_file_contents(file_path: str, patch_data: list, expected_hash: str) -> str`

Applies precise edits to a text file based on a list of changes. Validates against a provided file hash to prevent concurrent modification conflicts.

- **Example:**  
  ```python
  patch_text_file_contents(
      "example.txt",
      patch_data=[{"start_line": 2, "end_line": 3, "new_content": "Patched content."}],
      expected_hash="abc123"
  )
  ```

---