import sys
import os
import json
import win32com.client
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_outlook_automation_manager")

# Global variables for Outlook operations
outlook = None
namespace = None
recent_emails_cache = []

def initialize_outlook():
    """Initialize Outlook application and namespace. Must be called before any Outlook operation."""
    global outlook, namespace
    if not outlook or not namespace:
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Outlook: {str(e)}")

def get_folder_by_path(folder_path):
    """Get Outlook folder object by its path string.
    
    Args:
        folder_path (str): Folder path like "\\收件箱"
        
    Returns:
        Folder object if found, None otherwise
    """
    if not folder_path or folder_path == "\\":
        return namespace.Folders.Item(1)  # Default Inbox
    
    folders = folder_path.strip('\\').split('\\')
    current_folder = namespace.Folders.Item(1)  # Start with default mailbox
    
    for folder_name in folders:
        found = False
        for subfolder in current_folder.Folders:
            if subfolder.Name == folder_name:
                current_folder = subfolder
                found = True
                break
        if not found:
            raise ValueError(f"Folder not found: {folder_name}")
    
    return current_folder

@mcp.tool()
def list_folders() -> str:
    """
    List all available Outlook mail folders.
    
    Args:
        None
    
    Returns:
        JSON string containing a list of folder objects with name and path, like:
        [
          {"name": "收件箱", "path": "\\收件箱"},
          {"name": "已发送邮件", "path": "\\已发送邮件"},
          ...
        ]
    
    Raises:
        RuntimeError: If connection to Outlook fails
        ValueError: If folder structure cannot be accessed
    
    Example:
        >>> list_folders()
        '[{"name": "收件箱", "path": "\\\\收件箱"}]'
    """
    try:
        initialize_outlook()
        result = []
        
        # Get the root folder (default mailbox)
        root_folder = namespace.Folders.Item(1)
        
        # Add root folder itself
        result.append({
            "name": root_folder.Name,
            "path": f"\\{root_folder.Name}"
        })
        
        # Recursively add subfolders
        def process_subfolders(parent_folder, parent_path):
            sub_result = []
            for folder in parent_folder.Folders:
                current_path = f"{parent_path}\\{folder.Name}"
                sub_result.append({
                    "name": folder.Name,
                    "path": current_path
                })
                sub_result.extend(process_subfolders(folder, current_path))
            return sub_result
        
        result.extend(process_subfolders(root_folder, f"\\{root_folder.Name}"))
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error listing folders: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

@mcp.tool()
def list_recent_emails(days: int, folder_path: str = "\\收件箱") -> str:
    """
    Get recent emails from specified folder and cache them.
    
    Args:
        days (int): Number of days to look back (positive integer)
        folder_path (str): Path to folder (default is Inbox)
    
    Returns:
        JSON string containing list of email objects with subject, sender, date, like:
        [
          {
            "subject": "会议通知",
            "sender": "张三 <zhangsan@example.com>",
            "date": "2023-10-15T14:30:00Z"
          },
          ...
        ]
    
    Raises:
        ValueError: If days is not positive or folder not found
        RuntimeError: If email retrieval fails
    
    Example:
        >>> list_recent_emails(7, "\\收件箱")
        '[{"subject": "项目更新", "sender": "李四 <lisi@example.com>", "date": "2023-10-16T09:45:00Z"}]'
    """
    try:
        initialize_outlook()
        
        # Validate input parameters
        if days <= 0:
            raise ValueError("Days must be a positive number")
        
        # Get target folder
        folder = get_folder_by_path(folder_path)
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clear previous cache
        global recent_emails_cache
        recent_emails_cache = []
        
        # Retrieve emails
        items = folder.Items
        items.Sort("[ReceivedTime]", True)  # Sort by received time, newest first
        
        result = []
        for item in items:
            if hasattr(item, 'ReceivedTime'):
                received_time = item.ReceivedTime
                if isinstance(received_time, str):
                    try:
                        received_time = datetime.strptime(received_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                
                if received_time >= cutoff_date:
                    email_info = {
                        "subject": item.Subject,
                        "sender": str(item.Sender),
                        "date": received_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    result.append(email_info)
                    recent_emails_cache.append(item)  # Cache the full email object
                else:
                    break  # Stop when we pass the cutoff date
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error retrieving recent emails: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

@mcp.tool()
def search_emails(start_date: str, end_date: str, folder_path: str = "\\收件箱", contact: str = None, keyword: str = None) -> str:
    """
    Search emails by date range, contact or keyword.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        folder_path (str): Path to folder (default is Inbox)
        contact (str): Contact name or email address to filter by (optional)
        keyword (str): Keyword to search in subject or body (optional)
    
    Returns:
        JSON string containing list of matching emails with subject, sender, date
    
    Raises:
        ValueError: If dates are invalid or folder not found
        RuntimeError: If search operation fails
    
    Example:
        >>> search_emails("2023-10-10", "2023-10-17", contact="李四", keyword="项目")
        '[{"subject": "项目更新", "sender": "李四 <lisi@example.com>", "date": "2023-10-16T09:45:00Z"}]'
    """
    try:
        initialize_outlook()
        
        # Validate date inputs
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # Include entire end day
        except ValueError as ve:
            raise ValueError(f"Invalid date format: {str(ve)}. Please use YYYY-MM-DD format.")
        
        if start_dt > end_dt:
            raise ValueError("Start date must be before end date")
        
        # Get target folder
        folder = get_folder_by_path(folder_path)
        
        # Perform search
        items = folder.Items
        result = []
        
        # Build restriction filter
        filter_str = "[ReceivedTime] >= '{start}' AND [ReceivedTime] <= '{end}'".format(
            start=start_dt.strftime("%m/%d/%Y %H:%M %p"),
            end=end_dt.strftime("%m/%d/%Y %H:%M %p")
        )
        
        if contact:
            filter_str += f" AND ([SenderName] = '{contact}' OR [SenderEmailAddress] LIKE '%{contact}%')"
        
        if keyword:
            filter_str += f" AND ([Subject] LIKE '%{keyword}%' OR [Body] LIKE '%{keyword}%')"
        
        # Apply filter
        filtered_items = items.Restrict(filter_str)
        
        # Process results
        for item in filtered_items:
            if hasattr(item, 'ReceivedTime'):
                received_time = item.ReceivedTime
                if isinstance(received_time, str):
                    try:
                        received_time = datetime.strptime(received_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                
                email_info = {
                    "subject": item.Subject,
                    "sender": str(item.Sender),
                    "date": received_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                result.append(email_info)
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error searching emails: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

@mcp.tool()
def get_email_by_number(email_index: int) -> str:
    """
    Get detailed information about a specific email from recent list.
    
    Args:
        email_index (int): Index of email in the last retrieved list
    
    Returns:
        JSON string containing complete email info including subject, sender, date, body, attachments
    
    Raises:
        IndexError: If email index is out of range
        RuntimeError: If email details cannot be retrieved
    
    Example:
        >>> get_email_by_number(0)
        '{"subject": "合同签署确认", "sender": "王五 <wangwu@example.com>", "date": "2023-10-17T11:20:00Z", "body": "请尽快完成合同签署...", "attachments": [{"filename": "合同.pdf", "size": 245678}]}' 
    """
    try:
        initialize_outlook()
        
        # Check if there's cached email data
        if not recent_emails_cache:
            raise ValueError("No emails in cache. Please run list_recent_emails or search_emails first.")
        
        # Validate index
        if email_index < 0 or email_index >= len(recent_emails_cache):
            raise IndexError(f"Email index out of range (0-{len(recent_emails_cache)-1})")
        
        # Get email from cache
        email = recent_emails_cache[email_index]
        
        # Process attachments
        attachments = []
        if hasattr(email, 'Attachments') and email.Attachments.Count > 0:
            for attachment in email.Attachments:
                # Save attachment to temp directory
                temp_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'outlook_attachments')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, attachment.FileName)
                
                try:
                    attachment.SaveAsFile(file_path)
                    attachments.append({
                        "filename": attachment.FileName,
                        "size": attachment.Size,
                        "saved_path": file_path
                    })
                except Exception as ae:
                    print(f"Error saving attachment {attachment.FileName}: {str(ae)}")
        
        # Format email details
        email_details = {
            "subject": email.Subject,
            "sender": str(email.Sender),
            "date": email.ReceivedTime.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(email, 'ReceivedTime') else None,
            "body": email.Body,
            "attachments": attachments
        }
        
        return json.dumps(email_details, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error retrieving email details: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

@mcp.tool()
def reply_to_email_by_number(email_index: int, reply_content: str) -> str:
    """
    Reply to a specific email from recent list.
    
    Args:
        email_index (int): Index of email in the last retrieved list
        reply_content (str): Content to include in the reply
    
    Returns:
        JSON string confirming successful reply
    
    Raises:
        IndexError: If email index is out of range
        ValueError: If reply content is empty
        RuntimeError: If reply operation fails
    
    Example:
        >>> reply_to_email_by_number(0, "我已收到并会尽快处理。")
        '"回复邮件已成功发送。"'
    """
    try:
        initialize_outlook()
        
        # Check if there's cached email data
        if not recent_emails_cache:
            raise ValueError("No emails in cache. Please run list_recent_emails or search_emails first.")
        
        # Validate index
        if email_index < 0 or email_index >= len(recent_emails_cache):
            raise IndexError(f"Email index out of range (0-{len(recent_emails_cache)-1})")
        
        # Validate reply content
        if not reply_content or not reply_content.strip():
            raise ValueError("Reply content cannot be empty")
        
        # Get email from cache and create reply
        original_email = recent_emails_cache[email_index]
        reply_email = original_email.Reply()
        
        # Set reply content
        reply_email.Body = reply_content
        
        # Send the reply
        reply_email.Send()
        
        return json.dumps("回复邮件已成功发送。", ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error replying to email: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

@mcp.tool()
def compose_email(subject: str, body: str, to: str, cc: str = None) -> str:
    """
    Create and send a new email.
    
    Args:
        subject (str): Email subject line
        body (str): Email body text
        to (str): Recipient email address
        cc (str): Optional CC recipient address
    
    Returns:
        JSON string confirming successful delivery
    
    Raises:
        ValueError: If required fields are missing or invalid
        RuntimeError: If email sending fails
    
    Example:
        >>> compose_email("会议确认", "明天下午3点开会", "zhangsan@example.com")
        '"邮件已成功发送至 zhangsan@example.com。"'
    """
    try:
        initialize_outlook()
        
        # Validate required parameters
        if not subject or not subject.strip():
            raise ValueError("Subject cannot be empty")
        
        if not body or not body.strip():
            raise ValueError("Body cannot be empty")
        
        if not to or not to.strip():
            raise ValueError("To address cannot be empty")
        
        # Create new email
        mail_item = outlook.CreateItem(0)  # 0 represents a MailItem
        
        # Set email properties
        mail_item.Subject = subject
        mail_item.Body = body
        mail_item.To = to
        
        if cc:
            mail_item.CC = cc
        
        # Send the email
        mail_item.Send()
        
        return json.dumps(f"邮件已成功发送至 {to}。", ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()