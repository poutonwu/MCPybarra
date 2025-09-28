# mcp_outlook_manager

## Overview

The `mcp_outlook_manager` is a Model Context Protocol (MCP) server that provides integration with Microsoft Outlook. It enables external tools and language models to interact with Outlook for tasks such as listing folders, searching emails, reading messages, replying to emails, and composing new messages.

This server allows automation of common email-related workflows and supports rich querying capabilities over email content, time ranges, and folder structures.

---

## Installation

Before running the server, ensure you have Python 3.10 or higher installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** This server uses `win32com.client`, which requires Windows and Microsoft Outlook to be installed on the system.

---

## Running the Server

To start the MCP Outlook Manager server, run the following command from your terminal:

```bash
python outlook_server.py
```

This will launch the server using standard input/output (`stdio`) transport protocol.

---

## Available Tools

Below are the available tools exposed by this MCP server:

### `list_folders() -> str`

**Description**: Lists all available Outlook mail folders across all accounts.

**Returns**: A JSON-formatted list of folder names.

---

### `list_recent_emails(days: int, folder: str = None) -> str`

**Description**: Retrieves a list of recent email subject lines from the specified folder within the given number of days.

**Args**:
- `days`: Number of days to look back (must be non-negative).
- `folder`: Folder name to search in (optional, defaults to Inbox).

**Returns**: A JSON-formatted list of email subjects.

---

### `search_emails(keyword: str = None, contact: str = None, start_date: str = None, end_date: str = None, folder: str = None) -> str`

**Description**: Searches emails based on keyword, sender/receiver address, or date range in the specified folder.

**Args**:
- `keyword`: Search term in subject or body.
- `contact`: Email address or name to filter by.
- `start_date`: Start date for filtering (format: `YYYY-MM-DD`).
- `end_date`: End date for filtering (format: `YYYY-MM-DD`).
- `folder`: Folder name to search in (optional, defaults to Inbox).

**Returns**: A JSON-formatted list of matching email subjects.

---

### `get_email_by_number(email_number: int) -> str`

**Description**: Retrieves detailed information about a specific email from the last listed set.

**Args**:
- `email_number`: Index of the email in the previously listed results.

**Returns**: A JSON object containing subject, body, sender info, and attachment details.

---

### `reply_to_email_by_number(email_number: int, reply_content: str) -> str`

**Description**: Sends a reply to a specific email from the last listed set.

**Args**:
- `email_number`: Index of the email to reply to.
- `reply_content`: Content of the reply message.

**Returns**: A success or error message indicating whether the reply was sent.

---

### `compose_email(to: str, cc: str = None, subject: str = None, body: str = None, attachments: list = None) -> str`

**Description**: Composes and sends a new email with optional recipients, subject, body, and attachments.

**Args**:
- `to`: Comma-separated recipient addresses.
- `cc`: Optional comma-separated CC addresses.
- `subject`: Subject line of the email.
- `body`: Body content of the email.
- `attachments`: Optional list of file paths to attach.

**Returns**: A success or error message indicating whether the email was sent.