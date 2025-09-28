# mcp_outlook_email_manager

A MCP server that provides tools for managing Outlook emails through the Model Context Protocol.

## Overview

The `mcp_outlook_email_manager` server enables seamless integration between large language models (LLMs) and Microsoft Outlook, allowing for advanced email management capabilities such as listing folders, searching emails, reading messages, replying to emails, and composing new ones. This server uses the MCP protocol to expose these functions to LLMs in a structured and secure way.

## Installation

Before running the server, ensure you have Python 3.10+ installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

This will install the necessary packages including `mcp`, `pythoncom`, and `pywin32`.

> **Note**: This server only works on Windows systems with Microsoft Outlook installed and configured.

## Running the Server

To start the server, run the following command from the terminal or command prompt:

```bash
python mcp_outlook_email_manager.py
```

This starts the MCP server using standard input/output transport.

## Available Tools

Below is a list of available tools exposed by this server via the MCP protocol:

### `check_outlook_ready`
Checks if Outlook is accessible and ready for interaction. Returns version info or an error message if not ready.

### `list_folders`
Lists all available email folders in the current Outlook profile (e.g., "Inbox", "Sent Items").

### `list_recent_emails`
Fetches titles of emails received within a specified number of days from a given folder (default: Inbox).

### `search_emails`
Searches for emails within a date range in a specific folder, filtering by sender or keyword.

### `get_email_by_number`
Retrieves detailed content (subject, body, attachments) of an email by its index number from cached results.

### `reply_to_email_by_number`
Sends a reply to an email identified by its index number in the cached list.

### `compose_email`
Composes and sends a new email with subject, body, recipients, and optional CC addresses.