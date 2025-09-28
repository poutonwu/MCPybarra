import os
import sys
import json
import re
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
import win32com.client

# Initialize FastMCP server
mcp = FastMCP("mcp_outlook_email_manager")

# Shared cache for emails
cached_emails = []

def validate_folder_name(folder_name):
    """Validates the folder name provided.

    Args:
        folder_name: Name of the folder as a string.

    Raises:
        ValueError: If folder_name is not a non-empty string.
    """
    if not isinstance(folder_name, str) or not folder_name.strip():
        raise ValueError("Folder name must be a non-empty string.")

def validate_email_number(email_number):
    """Validates the email index number provided.

    Args:
        email_number: Index number of the email as an integer.

    Raises:
        ValueError: If email_number is not valid in the cached list.
    """
    if not isinstance(email_number, int) or email_number < 0 or email_number >= len(cached_emails):
        raise ValueError("Invalid email number.")

@mcp.tool()
def list_folders():
    """Lists all available Outlook email folders.

    Returns:
        A JSON string containing a list of folder names.

    Example:
        list_folders()
        Output: ["Inbox", "Sent Items", "CustomFolder1"]
    """
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        folders = [folder.Name for folder in namespace.Folders]
        return json.dumps(folders)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def list_recent_emails(days: int, folder_name: str = "Inbox"):
    """Fetches the titles of emails received within a specified number of days.

    Args:
        days: Number of days to look back for emails.
        folder_name: Name of the folder to filter emails (optional).

    Returns:
        A JSON string containing a list of email titles.

    Example:
        list_recent_emails(7, "Inbox")
        Output: ["Meeting Reminder", "Invoice Due"]
    """
    try:
        if days <= 0:
            raise ValueError("Days must be a positive integer.")
        validate_folder_name(folder_name)

        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        folder = None
        # Case-insensitive match for folder name
        for f in namespace.Folders:
            if f.Name.lower() == folder_name.lower():
                folder = f
                break
        if folder is None:
            raise ValueError(f"Folder '{folder_name}' not found.")

        cutoff_date = datetime.now() - timedelta(days=days)
        global cached_emails
        cached_emails = []

        for item in folder.Items:
            if item.ReceivedTime >= cutoff_date:
                cached_emails.append(item)

        email_titles = [email.Subject for email in cached_emails]
        return json.dumps(email_titles)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def search_emails(start_date: str, end_date: str, folder_name: str, filter_by: str):
    """Searches for emails within a specified time range and folder, filtering by sender or keyword.

    Args:
        start_date: Start date for the search in "YYYY-MM-DD" format.
        end_date: End date for the search in "YYYY-MM-DD" format.
        folder_name: Name of the folder to search in.
        filter_by: Filter criteria, either by sender's email or keyword.

    Returns:
        A JSON string containing a list of email titles matching the search criteria.

    Example:
        search_emails("2023-01-01", "2023-01-31", "Inbox", "john.doe@example.com")
        Output: ["Project Update", "Meeting Schedule"]
    """
    try:
        validate_folder_name(folder_name)
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_date > end_date:
            raise ValueError("Start date must be before end date.")

        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        folder = None
        # Case-insensitive match for folder name
        for f in namespace.Folders:
            if f.Name.lower() == folder_name.lower():
                folder = f
                break
        if folder is None:
            raise ValueError(f"Folder '{folder_name}' not found.")

        filtered_emails = []
        for item in folder.Items:
            if start_date <= item.ReceivedTime <= end_date:
                if filter_by.lower() in item.Subject.lower() or filter_by.lower() in item.SenderEmailAddress.lower():
                    filtered_emails.append(item.Subject)

        return json.dumps(filtered_emails)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_email_by_number(email_number: int):
    """Fetches detailed content and attachments for an email identified by its index.

    Args:
        email_number: The index number for the email in the cached list.

    Returns:
        A JSON string containing:
            - subject: Email subject.
            - body: Email body content.
            - attachments: List of attachment file names.

    Example:
        get_email_by_number(1)
        Output: {"subject": "Meeting Reminder", "body": "Details about the meeting...", "attachments": ["agenda.pdf"]}
    """
    try:
        if not cached_emails:
            raise ValueError("No emails are cached. Please run 'list_recent_emails' first.")
        validate_email_number(email_number)
        email = cached_emails[email_number]

        attachments = [attachment.FileName for attachment in email.Attachments]
        return json.dumps({"subject": email.Subject, "body": email.Body, "attachments": attachments})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def reply_to_email_by_number(email_number: int, reply_content: str):
    """Replies to an email identified by its index and sends the reply content.

    Args:
        email_number: The index number for the email in the cached list.
        reply_content: The content of the reply.

    Returns:
        A JSON string containing a success message.

    Example:
        reply_to_email_by_number(1, "Thank you for the update.")
        Output: "Reply sent successfully"
    """
    try:
        if not cached_emails:
            raise ValueError("No emails are cached. Please run 'list_recent_emails' first.")
        validate_email_number(email_number)
        email = cached_emails[email_number]

        reply = email.Reply()
        reply.Body = reply_content
        reply.Send()

        return json.dumps("Reply sent successfully")
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def compose_email(subject: str, body: str, recipients: list, cc: list = []):
    """Composes and sends a new email.

    Args:
        subject: Subject of the email.
        body: Body content of the email.
        recipients: List of recipient email addresses.
        cc: List of CC email addresses (optional).

    Returns:
        A JSON string containing a success message.

    Example:
        compose_email("Meeting Reminder", "Details about the meeting...", ["john.doe@example.com"], ["jane.doe@example.com"])
        Output: "Email sent successfully"
    """
    try:
        if not isinstance(recipients, list) or not all(isinstance(email, str) for email in recipients):
            raise ValueError("Recipients must be a list of email addresses.")
        if not recipients:
            raise ValueError("At least one recipient must be provided.")
        if not isinstance(cc, list) or not all(isinstance(email, str) for email in cc):
            raise ValueError("CC must be a list of email addresses.")

        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.Body = body
        mail.To = ";".join(recipients)
        mail.CC = ";".join(cc)
        mail.Send()

        return json.dumps("Email sent successfully")
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()