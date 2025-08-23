# MCP Tools Plan

This plan outlines the tools for an MCP server designed for automated Word document processing. The server will manage document lifecycle, content addition, text manipulation, table operations, and formatting. It will use the `python-docx` library as the core engine for all Word document interactions. A central `DocumentManager` class will be implemented to maintain the state of the currently active document, ensuring that operations are performed on the correct file.

| Function Name | Description | Parameters | Return Value |
| :--- | :--- | :--- | :--- |
| `create_document` | Creates a new, blank Word document in memory. This document becomes the active document. | `filename: str`: The desired path to save the new document to later. | `str`: A confirmation message, e.g., "New document created for '{filename}' and is now the active document." |
| `open_document` | Opens an existing Word document from the specified path, making it the active document for subsequent operations. | `path: str`: The full file path to the existing `.docx` document. | `str`: A confirmation message indicating the document is now active, e.g., "Document at '{path}' opened and is now active." |
| `save_document` | Saves the currently active document to the path it was created with or opened from. Fails if no document is active. | `None` | `str`: A confirmation message with the save path, e.g., "Document saved to '{path}'." |
| `save_as_document` | Saves the currently active document to a new specified path. The new path becomes the active path for future saves. | `new_path: str`: The new full file path to save the document to. | `str`: A confirmation message with the new save path, e.g., "Document saved to '{new_path}'." |
| `create_document_copy` | Creates a copy of an existing document at a new location. This does not change the currently active document. | `source_path: str`: The path of the document to copy. <br> `destination_path: str`: The path where the copy will be saved. | `str`: A confirmation message, e.g., "Copy of '{source_path}' created at '{destination_path}'." |
| `add_paragraph` | Adds a new paragraph of text to the end of the active document. | `text: str`: The content of the paragraph. | `str`: A confirmation message, e.g., "Paragraph added." |
| `add_heading` | Adds a heading to the end of the active document. | `text: str`: The text for the heading. <br> `level: int`: The heading level (0-9). Level 0 is a title. | `str`: A confirmation message, e.g., "Heading '{text}' added with level {level}." |
| `add_table` | Adds a new table with a specified number of rows and columns to the end of the active document. | `rows: int`: The number of rows in the table. <br> `cols: int`: The number of columns in the table. | `str`: A confirmation message, e.g., "Table with {rows} rows and {cols} columns added. It is now the active table." |
| `add_page_break` | Inserts a page break at the end of the active document. | `None` | `str`: "Page break added." |
| `get_document_info` | Retrieves metadata about the active document. | `None` | `dict`: A dictionary containing document properties like `title`, `author`, `created_date`, `modified_date`, and `path`. |
| `search_text` | Searches for all occurrences of a given text string in the active document and returns their locations. | `query: str`: The text to search for. | `list[str]`: A list of strings, where each string describes the location of an occurrence (e.g., "Found in paragraph 5", "Found in table 2, row 3, col 1"). |
| `search_and_replace` | Finds all occurrences of a search string within the active document and replaces them with a new string. | `old_text: str`: The text to find. <br> `new_text: str`: The text to replace it with. | `str`: A message reporting how many replacements were made, e.g., "Replaced {count} occurrences of '{old_text}'." |
| `delete_paragraph` | Deletes a paragraph by its index (0-based). | `paragraph_index: int`: The index of the paragraph to delete. | `str`: A confirmation message, e.g., "Paragraph at index {paragraph_index} has been deleted." |
| `delete_text` | Deletes all occurrences of a specific text string from the document by replacing it with an empty string. | `text_to_delete: str`: The text to find and delete. | `str`: A message reporting how many occurrences were deleted, e.g., "Deleted {count} occurrences of '{text_to_delete}'." |
| `add_table_row` | Adds a new row to the specified table. If no table index is given, it targets the last table added. | `table_index: int`: The 0-based index of the target table in the document. | `str`: A confirmation message, e.g., "Row added to table {table_index}." |
| `delete_table_row` | Deletes a row from a specified table by its index. | `table_index: int`: The 0-based index of the target table. <br> `row_index: int`: The 0-based index of the row to delete. | `str`: A confirmation message, e.g., "Row {row_index} deleted from table {table_index}." |
| `edit_table_cell` | Edits the text content of a specific cell in a table. | `table_index: int`: The 0-based index of the target table. <br> `row: int`: The 0-based row index of the cell. <br> `col: int`: The 0-based column index of the cell. <br> `text: str`: The new text to place in the cell. | `str`: A confirmation message, e.g., "Cell ({row}, {col}) in table {table_index} updated." |
| `merge_table_cells` | Merges a rectangular region of cells in a table into a single cell. | `table_index: int`: The 0-based index of the target table. <br> `start_row: int`: The starting row index of the merge. <br> `start_col: int`: The starting column index of the merge. <br> `end_row: int`: The ending row index of the merge. <br> `end_col: int`: The ending column index of the merge. | `str`: A confirmation message describing the merged region. |
| `split_table` | Splits an existing table into two at a specified row. The specified row becomes the first row of the new table. | `table_index: int`: The 0-based index of the table to split. <br> `row_index: int`: The 0-based index of the row where the split should occur. | `str`: A confirmation message, e.g., "Table {table_index} was split at row {row_index}." |
| `set_page_margins` | Sets the page margins for all sections in the active document. | `top: float`: Top margin in inches. <br> `bottom: float`: Bottom margin in inches. <br> `left: float`: Left margin in inches. <br> `right: float`: Right margin in inches. | `str`: "Page margins have been set." |
| `replace_section` | Finds a section by its heading text and replaces all content between it and the next heading of the same or higher level. | `heading_text: str`: The exact text of the heading that marks the start of the section. <br> `new_content: str`: The new paragraph text to insert as the section's content. | `str`: A confirmation or error message, e.g., "Section '{heading_text}' content replaced." or "Heading '{heading_text}' not found." |
| `edit_section_by_keyword` | Finds the first paragraph containing a keyword, identifies its section (bounded by headings), and appends new content to that section. | `keyword: str`: The keyword to locate within a paragraph. <br> `new_content: str`: The new paragraph text to append to the section. | `str`: A confirmation or error message, e.g., "Content added to section containing keyword '{keyword}'." or "Keyword '{keyword}' not found." |

# Server Overview

The server will provide a comprehensive suite of tools for the automated processing and manipulation of Microsoft Word (`.docx`) documents. It will enable users to perform file operations (create, open, save, copy), add and format content (paragraphs, headings, tables, page breaks), retrieve document information, perform advanced text search and replacement, and execute complex operations on tables and document sections.

# File to be Generated

The entire server logic, including the MCP tool definitions and the underlying `DocumentManager` class, will be contained within a single Python file.

-   `mcp_word_server.py`

# Dependencies

The following third-party Python library will be required for the implementation.

-   `python-docx`: To handle all creation, reading, and writing of `.docx` files.