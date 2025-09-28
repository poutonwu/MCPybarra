import sys
import win32com.client
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_outlook_email_manager")

# Outlook application object
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# Cache for storing email metadata
email_cache = []

@mcp.tool()
def list_folders() -> list:
    """
    Lists all available Outlook mail folders.

    Returns:
        A list of folder names (strings).
    """
    try:
        folders = []
        for folder in outlook.Folders:
            folders.append(folder.Name)
        return folders
    except Exception as e:
        raise Exception(f"Failed to list folders: {str(e)}")

@mcp.tool()
def list_recent_emails(days: int, folder_name: str = "Inbox") -> list:
    """
    Retrieves email titles from a specified folder within a given number of days. Caches email metadata.

    Args:
        days: Number of days to look back.
        folder_name: Specific folder name (default: Inbox).

    Returns:
        A list of dictionaries containing 'subject', 'sender', and 'received_time' for each email.
    """
    try:
        global email_cache
        email_cache = []
        folder = outlook.GetDefaultFolder(6) if folder_name == "Inbox" else outlook.Folders.Item(folder_name)
        emails = folder.Items
        emails.Sort("[ReceivedTime]", True)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = []
        for email in emails:
            # Handle ReceivedTime properly
            try:
                received_time = email.ReceivedTime
            except AttributeError:
                continue  # Skip emails where ReceivedTime is inaccessible
            
            if received_time >= cutoff_date:
                email_cache.append({
                    "subject": email.Subject,
                    "sender": email.SenderName,
                    "received_time": received_time.strftime("%Y-%m-%d %H:%M:%S") if received_time else "Unknown",
                    "body": email.Body,
                    "attachments": [attachment.FileName for attachment in email.Attachments]
                })
                result.append({
                    "subject": email.Subject,
                    "sender": email.SenderName,
                    "received_time": received_time.strftime("%Y-%m-%d %H:%M:%S") if received_time else "Unknown"
                })
        return result
    except Exception as e:
        raise Exception(f"Failed to list recent emails: {str(e)}")

@mcp.tool()
def search_emails(query: str, start_date: str = None, end_date: str = None, folder_name: str = "Inbox") -> list:
    """
    Searches emails by keyword or sender within a specified time range and folder.

    Args:
        query: Keyword or sender name.
        start_date: Start date in 'YYYY-MM-DD' format.
        end_date: End date in 'YYYY-MM-DD' format.
        folder_name: Folder to search (default: Inbox).

    Returns:
        A list of dictionaries with 'subject', 'sender', and 'received_time'.
    """
    try:
        folder = outlook.GetDefaultFolder(6) if folder_name == "Inbox" else outlook.Folders.Item(folder_name)
        emails = folder.Items
        emails.Sort("[ReceivedTime]", True)
        
        # Input validation
        if not query or query.strip() == "":
            raise ValueError("Query cannot be empty")
        
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # Include entire end date
        
        result = []
        for email in emails:
            # Handle ReceivedTime properly
            try:
                received_time = email.ReceivedTime
            except AttributeError:
                continue  # Skip emails where ReceivedTime is inaccessible
            
            if (not start_date or received_time >= start_date) and \
               (not end_date or received_time < end_date) and \
               (query.lower() in email.Subject.lower() or query.lower() in email.SenderName.lower()):
                result.append({
                    "subject": email.Subject,
                    "sender": email.SenderName,
                    "received_time": received_time.strftime("%Y-%m-%d %H:%M:%S") if received_time else "Unknown"
                })
        return result
    except Exception as e:
        raise Exception(f"Failed to search emails: {str(e)}")

@mcp.tool()
def get_email_by_number(email_number: int) -> dict:
    """
    Retrieves the full content (body + attachments) of an email from the cached list.

    Args:
        email_number: Index of the email in the last retrieved list.

    Returns:
        A dictionary with 'subject', 'sender', 'body', and 'attachments' (list of file paths).
    """
    try:
        if email_number < 0 or email_number >= len(email_cache):
            raise ValueError("Invalid email number")
        return email_cache[email_number]
    except Exception as e:
        raise Exception(f"Failed to get email by number: {str(e)}")

@mcp.tool()
def reply_to_email_by_number(email_number: int, reply_text: str) -> str:
    """
    Replies to a specific email (by index) with a given message.

    Args:
        email_number: Index of the email in the last retrieved list.
        reply_text: The reply message.

    Returns:
        Confirmation message (success/failure).
    """
    try:
        if email_number < 0 or email_number >= len(email_cache):
            raise ValueError("Invalid email number")
        
        cached_email = email_cache[email_number]
        folder = outlook.GetDefaultFolder(6)
        emails = folder.Items
        emails.Sort("[ReceivedTime]", True)
        
        for email in emails:
            try:
                received_time = email.ReceivedTime
            except AttributeError:
                continue  # Skip emails where ReceivedTime is inaccessible
            
            if (email.Subject == cached_email["subject"] and 
                email.SenderName == cached_email["sender"] and 
                received_time.strftime("%Y-%m-%d %H:%M:%S") == cached_email["received_time"]):
                reply = email.Reply()
                reply.Body = reply_text
                reply.Send()
                return "Reply sent successfully"
        return "Email not found"
    except Exception as e:
        raise Exception(f"Failed to reply to email: {str(e)}")

@mcp.tool()
def compose_email(subject: str, body: str, recipients: list, cc: list = None) -> str:
    """
    Creates and sends a new email.

    Args:
        subject: Email subject.
        body: Email body.
        recipients: List of recipient email addresses.
        cc: List of CC recipients.

    Returns:
        Confirmation message (success/failure).
    """
    try:
        if not recipients or len(recipients) == 0:
            raise ValueError("At least one recipient is required")
            
        mail = outlook.Application.CreateItem(0)
        mail.Subject = subject
        mail.Body = body
        mail.To = "; ".join(recipients)
        if cc:
            mail.CC = "; ".join(cc)
        mail.Send()
        return "Email sent successfully"
    except Exception as e:
        raise Exception(f"Failed to compose email: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()