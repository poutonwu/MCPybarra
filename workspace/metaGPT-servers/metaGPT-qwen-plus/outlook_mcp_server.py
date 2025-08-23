import sys
from mcp.server.fastmcp import FastMCP
import win32com.client
from datetime import datetime, timedelta

# 初始化 FastMCP 服务器
mcp = FastMCP("outlook")

# Outlook 连接初始化
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# 邮件缓存
email_cache = []

@mcp.tool()
def list_folders() -> dict:
    """
    列出所有可用的Outlook邮件文件夹。

    Returns:
        包含文件夹名称和路径的字典列表。
    """
    folders = []
    for folder in outlook.Folders:
        folders.append({"name": folder.Name, "path": folder.FolderPath})
    return {"folders": folders}

@mcp.tool()
def list_recent_emails(days: int = 7, folder_name: str = None) -> dict:
    """
    获取指定天数内最近的邮件标题列表。

    Args:
        days: 需要检索的过去天数，默认为7天。
        folder_name: 指定的邮件文件夹名称，如果为空则使用默认收件箱。

    Returns:
        包含邮件主题、发件人和接收时间的字典列表。
    """
    global email_cache

    # 获取收件箱
    inbox = outlook.GetDefaultFolder(6)  # 6 是收件箱的代码
    if folder_name:
        for folder in outlook.Folders:
            if folder.Name == folder_name:
                inbox = folder
                break

    # 时间范围计算
    target_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    filter_criteria = f"[ReceivedTime] >= '{target_date}'"

    # 应用筛选器并获取邮件
    items = inbox.Items.Restrict(filter_criteria)
    items.Sort("[ReceivedTime]", True)

    emails = []
    email_cache = []
    for index, item in enumerate(items):
        try:
            email_data = {
                "id": index,
                "subject": item.Subject,
                "sender": item.SenderName,
                "received_time": item.ReceivedTime.strftime('%Y-%m-%d %H:%M'),
                "body": item.Body,
                "attachments": [attachment.FileName for attachment in item.Attachments]
            }
            emails.append({
                "id": index,
                "subject": item.Subject,
                "sender": item.SenderName,
                "received_time": item.ReceivedTime.strftime('%Y-%m-%d %H:%M')
            })
            email_cache.append(email_data)
        except Exception as e:
            continue  # 忽略个别无法处理的邮件

    return {"emails": emails}

@mcp.tool()
def search_emails(query: str, folder_name: str = None, start_date: str = None, end_date: str = None) -> dict:
    """
    在指定时间段和文件夹内按联系人或关键词搜索邮件。

    Args:
        query: 搜索查询字符串，可以是联系人或关键词。
        folder_name: 指定的邮件文件夹名称，如果为空则使用默认收件箱。
        start_date: 搜索的起始日期（格式：YYYY-MM-DD HH:MM）。
        end_date: 搜索的结束日期（格式：YYYY-MM-DD HH:MM）。

    Returns:
        包含匹配邮件主题、发件人和接收时间的字典列表。
    """
    global email_cache

    # 获取收件箱
    inbox = outlook.GetDefaultFolder(6)  # 6 是收件箱的代码
    if folder_name:
        for folder in outlook.Folders:
            if folder.Name == folder_name:
                inbox = folder
                break

    # 构建筛选条件
    filter_criteria = f"[Subject] like '%{query}%' or [SenderName] like '%{query}%'"

    if start_date:
        filter_criteria += f" and [ReceivedTime] >= '{start_date}'"
    if end_date:
        filter_criteria += f" and [ReceivedTime] <= '{end_date}'"

    # 应用筛选器并获取邮件
    items = inbox.Items.Restrict(filter_criteria)
    items.Sort("[ReceivedTime]", True)

    emails = []
    email_cache = []
    for index, item in enumerate(items):
        try:
            email_data = {
                "id": index,
                "subject": item.Subject,
                "sender": item.SenderName,
                "received_time": item.ReceivedTime.strftime('%Y-%m-%d %H:%M'),
                "body": item.Body,
                "attachments": [attachment.FileName for attachment in item.Attachments]
            }
            emails.append({
                "id": index,
                "subject": item.Subject,
                "sender": item.SenderName,
                "received_time": item.ReceivedTime.strftime('%Y-%m-%d %H:%M')
            })
            email_cache.append(email_data)
        except Exception as e:
            continue  # 忽略个别无法处理的邮件

    return {"emails": emails}

@mcp.tool()
def get_email_by_number(email_id: int) -> dict:
    """
    获取指定编号的邮件详细信息。

    Args:
        email_id: 邮件的唯一标识符。

    Returns:
        包含邮件正文和附件信息的字典。
    """
    global email_cache

    if email_id < 0 or email_id >= len(email_cache):
        raise ValueError(f"无效的邮件ID: {email_id}")

    email = email_cache[email_id]
    return {
        "subject": email["subject"],
        "sender": email["sender"],
        "received_time": email["received_time"],
        "body": email["body"],
        "attachments": email["attachments"]
    }

@mcp.tool()
def reply_to_email_by_number(email_id: int, reply_text: str) -> dict:
    """
    对指定编号的邮件进行回复。

    Args:
        email_id: 邮件的唯一标识符。
        reply_text: 回复邮件的内容。

    Returns:
        包含回复结果的状态消息。
    """
    global email_cache

    if email_id < 0 or email_id >= len(email_cache):
        raise ValueError(f"无效的邮件ID: {email_id}")

    original_email = email_cache[email_id]
    
    # 创建新的邮件对象并填充回复内容
    mail = outlook.Session.CreateItem(0)  # 0 表示邮件项
    mail.Subject = 'RE: ' + original_email["subject"]
    mail.Body = reply_text + '\n\n--- 原始邮件 ---\n' + original_email["body"]
    mail.To = original_email["sender"]  # 发送回原发件人
    mail.Send()

    return {"status": "success", "message": f"已回复邮件: {original_email['subject']}", "to": original_email["sender"]}

@mcp.tool()
def compose_email(subject: str, body: str, to: str, cc: str = None) -> dict:
    """
    新建并发送一封新邮件。

    Args:
        subject: 邮件的主题。
        body: 邮件正文内容。
        to: 收件人邮箱地址。
        cc: 抄送邮箱地址（可选）。

    Returns:
        包含发送结果的状态消息。
    """
    # 创建新的邮件对象并填充内容
    mail = outlook.Session.CreateItem(0)  # 0 表示邮件项
    mail.Subject = subject
    mail.Body = body
    mail.To = to
    if cc:
        mail.CC = cc
    mail.Send()

    return {"status": "success", "message": f"邮件已发送给: {to}", "subject": subject}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()