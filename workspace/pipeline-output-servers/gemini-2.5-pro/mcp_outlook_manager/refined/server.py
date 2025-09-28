import sys
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Ensure compatibility with different Python environments
try:
    import win32com.client
except ImportError:
    print("Error: The 'pywin32' library is not installed. Please install it using 'pip install pywin32'.")
    sys.exit(1)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: The 'mcp' library is not installed. Please install it using 'pip install mcp'.")
    sys.exit(1)

# --- Server Initialization ---
mcp = FastMCP("mcp_outlook_server")

# --- In-memory Cache ---
# A simple cache to store the results of the last email listing or search.
# The key is the assigned number, and the value is the win32com MailItem object.
email_cache: Dict[int, Any] = {}

class OutlookManager:
    """
    A manager class to encapsulate all interactions with the Outlook application.
    This helps in separating the core logic from the MCP tool definitions,
    improving modularity and maintainability.
    """
    def __init__(self):
        try:
            # Attempt to get a running instance of Outlook
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
        except Exception as e:
            # Provide a helpful error message if Outlook is not running or accessible
            raise ConnectionError(f"Failed to connect to Outlook. Please ensure Outlook is running. Details: {e}")

    def _get_folder(self, folder_name: str) -> Any:
        """
        Retrieves a specific folder object from Outlook by its name.
        """
        try:
            # First attempt: Try accessing directly from the default Inbox
            inbox = self.namespace.GetDefaultFolder(6)
            if inbox.Name.lower() == folder_name.lower():
                return inbox
            # Check subfolders of Inbox
            for subfolder in inbox.Folders:
                if subfolder.Name.lower() == folder_name.lower():
                    return subfolder
        except Exception:
            pass

        try:
            # Second attempt: Try accessing directly from the Sent Items
            sent_items = self.namespace.GetDefaultFolder(5)
            if sent_items.Name.lower() == folder_name.lower():
                return sent_items
            # Check subfolders of Sent Items
            for subfolder in sent_items.Folders:
                if subfolder.Name.lower() == folder_name.lower():
                    return subfolder
        except Exception:
            pass

        # Third attempt: Iterate through all top-level folders
        for i in range(1, 25):  # Iterate through standard folder types
            try:
                folder = self.namespace.GetDefaultFolder(i)
                if folder.Name.lower() == folder_name.lower():
                    return folder
                # Check subfolders as well
                for subfolder in folder.Folders:
                    if subfolder.Name.lower() == folder_name.lower():
                        return subfolder
            except Exception:
                continue

        # Final attempt: Search across all stores (for localized or non-default folders)
        for store in self.namespace.Stores:
            try:
                root_folder = store.GetRootFolder()
                if root_folder.Name.lower() == folder_name.lower():
                    return root_folder
                # Recursively check subfolders in the store
                result = self._search_subfolders(root_folder, folder_name)
                if result:
                    return result
            except Exception:
                continue

        raise FileNotFoundError(f"Folder '{folder_name}' not found in Outlook.")

    def _search_subfolders(self, folder, target_name):
        """Helper method to recursively search subfolders."""
        try:
            for subfolder in folder.Folders:
                if subfolder.Name.lower() == target_name.lower():
                    return subfolder
                # Recursive call to check deeper levels
                result = self._search_subfolders(subfolder, target_name)
                if result:
                    return result
        except Exception:
            pass
        return None

    def list_all_folders(self) -> List[str]:
        """
        Retrieves a list of all accessible folder names in the main mailbox.
        """
        folders = []
        # First, add known default folders by their localized names
        try:
            folders.append(self.namespace.GetDefaultFolder(6).Name)  # Inbox
            folders.append(self.namespace.GetDefaultFolder(5).Name)  # Sent Items
            folders.append(self.namespace.GetDefaultFolder(4).Name)  # Drafts
            folders.append(self.namespace.GetDefaultFolder(3).Name)  # Outbox
            folders.append(self.namespace.GetDefaultFolder(2).Name)  # Deleted Items
        except Exception:
            pass

        # Then iterate through all possible folder types and their subfolders
        for i in range(1, 25):  # Iterate through standard folder types
            try:
                folder = self.namespace.GetDefaultFolder(i)
                if folder.Name not in folders:
                    folders.append(folder.Name)
                # Check subfolders as well
                for subfolder in folder.Folders:
                    if subfolder.Name not in folders:
                        folders.append(subfolder.Name)
            except Exception:
                continue

        # Finally, search across all stores for additional folders
        for store in self.namespace.Stores:
            try:
                root_folder = store.GetRootFolder()
                if root_folder.Name not in folders:
                    folders.append(root_folder.Name)
                # Recursively check subfolders
                self._collect_all_subfolders(root_folder, folders)
            except Exception:
                continue

        return sorted(set(folders))

    def _collect_all_subfolders(self, folder, folder_list):
        """Helper method to recursively collect all subfolders."""
        try:
            for subfolder in folder.Folders:
                if subfolder.Name not in folder_list:
                    folder_list.append(subfolder.Name)
                # Recursive call to collect deeper levels
                self._collect_all_subfolders(subfolder, folder_list)
        except Exception:
            pass

    def list_emails(self, folder_name: str, days: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists or searches for emails in a specified folder based on given criteria.
        """
        global email_cache
        email_cache.clear()  # Clear previous results

        folder = self._get_folder(folder_name)
        emails = folder.Items
        emails.Sort("[ReceivedTime]", True)  # Sort by received time, descending

        # Build filter string
        filter_parts = []
        if days:
            start_time = datetime.now() - timedelta(days=days)
            filter_parts.append(f"[ReceivedTime] >= '{start_time.strftime('%m/%d/%Y %H:%M %p')}'")
        elif start_date and end_date:
            filter_parts.append(f"[ReceivedTime] >= '{start_date} 00:00'")
            filter_parts.append(f"[ReceivedTime] <= '{end_date} 23:59'")

        if query:
            # DASL queries are more robust than SQL-like queries for text searching
            query_filter = f"urn:schemas:httpmail:subject LIKE '%{query}%' OR urn:schemas:httpmail:from LIKE '%{query}%' OR urn:schemas:httpmail:textdescription LIKE '%{query}%'"
            filter_parts.append(f"@SQL=({query_filter})")

        if filter_parts:
            filter_str = " AND ".join(filter_parts)
            emails = emails.Restrict(filter_str)

        results = []
        for i, email in enumerate(emails):
            if i >= 100: break  # Limit results to prevent performance issues
            email_number = i + 1
            email_cache[email_number] = email
            results.append({"number": email_number, "subject": email.Subject, "from": getattr(email, 'SenderName', 'N/A'), "received": email.ReceivedTime.strftime('%Y-%m-%d %H:%M')})

        return results

    def get_email_details(self, email_number: int) -> Dict[str, Any]:
        """
        Retrieves detailed information for a cached email by its number.
        """
        if email_number not in email_cache:
            raise ValueError(f"Invalid email number: {email_number}. Please run list_recent_emails or search_emails first.")

        email = email_cache[email_number]
        attachments = [att.FileName for att in email.Attachments]

        return {
            "from": getattr(email, 'SenderName', 'N/A'),
            "to": getattr(email, 'To', 'N/A'),
            "cc": getattr(email, 'CC', 'N/A'),
            "subject": getattr(email, 'Subject', 'N/A'),
            "received": email.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S'),
            "body": getattr(email, 'Body', 'N/A'),
            "attachments": attachments
        }

    def reply_to_email(self, email_number: int, reply_body: str) -> str:
        """
        Creates and sends a reply to a cached email.
        """
        if email_number not in email_cache:
            raise ValueError(f"Invalid email number: {email_number}. Please run list_recent_emails or search_emails first.")

        original_email = email_cache[email_number]
        reply = original_email.ReplyAll()
        reply.Body = reply_body + "\n\n" + reply.Body  # Prepend new body content
        reply.Send()
        return f"Successfully replied to email number {email_number}."

    def create_email(self, subject: str, body: str, recipients: List[str], cc_recipients: Optional[List[str]] = None) -> str:
        """
        Composes and sends a new email.
        """
        mail = self.outlook.CreateItem(0)  # 0 represents a MailItem
        mail.Subject = subject
        mail.Body = body
        mail.To = ";".join(recipients)
        if cc_recipients:
            mail.CC = ";".join(cc_recipients)
        mail.Send()
        return f"Email with subject '{subject}' sent successfully."

# --- MCP Tool Definitions ---

@mcp.tool()
def list_folders() -> str:
    """
    Retrieves and lists all accessible email folders from the user's main Outlook mailbox.
    This function scans the default mailbox for top-level folders and their direct subfolders,
    providing a comprehensive list for use in other email-related functions.

    Returns:
        str: A JSON string representing a sorted list of folder names.
             Example: '["Inbox", "Sent Items", "Drafts", "My Project Folder"]'
    """
    try:
        manager = OutlookManager()
        folders = manager.list_all_folders()
        return json.dumps(folders)
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
def list_recent_emails(days: int, folder_name: str = "Inbox") -> str:
    """
    Fetches a list of email summaries from a specified folder received within a given number of days.
    The results are cached, and each email is assigned a number for subsequent operations like 'get_email_by_number'.
    The list is sorted with the most recent emails first and is limited to the top 100 results for performance.

    Args:
        days (int): The number of past days to search for emails. Must be a positive integer.
        folder_name (str, optional): The name of the Outlook folder to search in. Defaults to "Inbox".

    Returns:
        str: A JSON string representing a list of dictionaries, where each dictionary contains the
             assigned number, subject, sender, and received time of an email. Returns an empty list if no emails are found.
             Example: '[{"number": 1, "subject": "Project Update", "from": "John Doe", "received": "2023-10-27 10:30"}]'
    """
    if not isinstance(days, int) or days <= 0:
        return json.dumps({"error": "Parameter 'days' must be a positive integer."})
    try:
        manager = OutlookManager()
        emails = manager.list_emails(folder_name=folder_name, days=days)
        return json.dumps(emails)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
def search_emails(query: str, start_date: str, end_date: str, folder_name: str = "Inbox") -> str:
    """
    Searches for emails based on a keyword within a specified date range and folder.
    The search query is applied to the email's subject, body, and sender fields.
    The results are cached, and each email is assigned a number for subsequent operations.
    The list is sorted with the most recent emails first and is limited to the top 100 results.

    Args:
        query (str): The keyword or phrase to search for.
        start_date (str): The start date for the search range, formatted as 'YYYY-MM-DD'.
        end_date (str): The end date for the search range, formatted as 'YYYY-MM-DD'.
        folder_name (str, optional): The name of the folder to search. Defaults to "Inbox".

    Returns:
        str: A JSON string representing a list of dictionaries, each containing the assigned number,
             subject, sender, and received time of a matching email. Returns an empty list if no matches are found.
             Example: '[{"number": 1, "subject": "Re: Project Plan", "from": "Jane Smith", "received": "2023-10-26 15:00"}]'
    """
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return json.dumps({"error": "Invalid date format. Please use 'YYYY-MM-DD'."})
    try:
        manager = OutlookManager()
        emails = manager.list_emails(folder_name=folder_name, start_date=start_date, end_date=end_date, query=query)
        return json.dumps(emails)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
def get_email_by_number(email_number: int) -> str:
    """
    Retrieves the full details of a specific email from the cache generated by
    `list_recent_emails` or `search_emails`, using its assigned number.
    This provides access to the sender, recipients, subject, full body, and attachments.

    Args:
        email_number (int): The number of the email as provided in the last list. Must be a positive integer.

    Returns:
        str: A JSON string representing a dictionary with the email's details, including sender,
             recipients (To, CC), subject, body, received time, and a list of attachment filenames.
             Returns an error message if the number is invalid or not found in the cache.
             Example: '{"from": "sender@example.com", "to": "you@example.com", "cc": "manager@example.com", "subject": "Project Update", "received": "2023-10-27 10:30:00", "body": "Here is the latest update...", "attachments": ["report.docx", "data.xlsx"]}'
    """
    if not isinstance(email_number, int) or email_number <= 0:
        return json.dumps({"error": "Parameter 'email_number' must be a positive integer."})
    try:
        manager = OutlookManager()
        details = manager.get_email_details(email_number)
        return json.dumps(details)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
def reply_to_email_by_number(email_number: int, reply_body: str) -> str:
    """
    Sends a 'Reply All' to a specific email from the cached list using its assigned number.
    The provided reply text is prepended to the original email's body in the reply.

    Args:
        email_number (int): The number of the email to reply to, from the cached list.
        reply_body (str): The content of the reply message. Cannot be empty.

    Returns:
        str: A JSON string containing a status message confirming the action.
             Example: '{"status": "Successfully replied to email number 1."}'
    """
    if not isinstance(email_number, int) or email_number <= 0:
        return json.dumps({"error": "Parameter 'email_number' must be a positive integer."})
    if not reply_body or not reply_body.strip():
        return json.dumps({"error": "Parameter 'reply_body' cannot be empty."})
    try:
        manager = OutlookManager()
        result = manager.reply_to_email(email_number, reply_body)
        return json.dumps({"status": result})
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Failed to send reply. Details: {e}"})

@mcp.tool()
def compose_email(subject: str, body: str, recipients: List[str], cc_recipients: Optional[List[str]] = None) -> str:
    """
    Composes and sends a new email with the specified subject, body, and recipients.

    Args:
        subject (str): The subject line of the new email. Cannot be empty.
        body (str): The main content of the email. Cannot be empty.
        recipients (List[str]): A list of one or more email addresses for the 'To' field.
        cc_recipients (List[str], optional): A list of email addresses for the 'CC' field. Defaults to None.

    Returns:
        str: A JSON string containing a status message confirming that the email was sent.
             Example: '{"status": "Email with subject 'New Proposal' sent successfully."}'
    """
    if not subject or not subject.strip():
        return json.dumps({"error": "Parameter 'subject' cannot be empty."})
    if not body or not body.strip():
        return json.dumps({"error": "Parameter 'body' cannot be empty."})
    if not recipients:
        return json.dumps({"error": "Parameter 'recipients' list cannot be empty."})
    try:
        manager = OutlookManager()
        result = manager.create_email(subject, body, recipients, cc_recipients)
        return json.dumps({"status": result})
    except Exception as e:
        return json.dumps({"error": f"Failed to send email. Details: {e}"})

# --- Main Execution Block ---
if __name__ == "__main__":
    # Set encoding to UTF-8 for cross-platform compatibility
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Run the MCP server
    mcp.run()