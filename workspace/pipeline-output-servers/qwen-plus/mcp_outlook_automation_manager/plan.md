# MCP Outlook Server Implementation Plan

## MCP Tools Plan

### 1. `list_folders` 工具
- **Function Name**: `list_folders`
- **Description**: 列出本地Outlook中所有可用的邮件文件夹。
- **Parameters**:
  - None
- **Return Value**:
  - 返回一个包含文件夹名称和路径的列表，格式为：
    ```json
    [
      {"name": "收件箱", "path": "\\收件箱"},
      {"name": "已发送邮件", "path": "\\已发送邮件"},
      ...
    ]
    ```

---

### 2. `list_recent_emails` 工具
- **Function Name**: `list_recent_emails`
- **Description**: 获取指定天数内特定文件夹中的邮件标题列表，并缓存邮件信息。
- **Parameters**:
  - `days`: 整数类型，表示获取最近多少天内的邮件（必填）。
  - `folder_path`: 字符串类型，表示要查询的文件夹路径（可选，默认为收件箱）。
- **Return Value**:
  - 返回一个包含邮件标题、发件人、日期等基本信息的列表，格式为：
    ```json
    [
      {
        "subject": "会议通知",
        "sender": "张三 <zhangsan@example.com>",
        "date": "2023-10-15T14:30:00Z"
      },
      ...
    ]
    ```
  - 同时在内存中缓存完整的邮件对象以供后续操作使用。

---

### 3. `search_emails` 工具
- **Function Name**: `search_emails`
- **Description**: 按联系人或关键词在指定时间段和文件夹内搜索邮件，并返回匹配邮件标题列表。
- **Parameters**:
  - `start_date`: 字符串类型，表示开始时间（格式：YYYY-MM-DD，必填）。
  - `end_date`: 字符串类型，表示结束时间（格式：YYYY-MM-DD，必填）。
  - `folder_path`: 字符串类型，表示要查询的文件夹路径（可选，默认为收件箱）。
  - `contact`: 字符串类型，表示按联系人搜索（可选）。
  - `keyword`: 字符串类型，表示按关键词搜索（可选）。
- **Return Value**:
  - 返回一个包含邮件标题、发件人、日期等基本信息的列表，格式为：
    ```json
    [
      {
        "subject": "项目更新",
        "sender": "李四 <lisi@example.com>",
        "date": "2023-10-16T09:45:00Z"
      },
      ...
    ]
    ```

---

### 4. `get_email_by_number` 工具
- **Function Name**: `get_email_by_number`
- **Description**: 获取上次列出的邮件的详细内容，包括正文和附件信息。
- **Parameters**:
  - `email_index`: 整数类型，表示邮件在最近一次列出的邮件列表中的索引位置（必填）。
- **Return Value**:
  - 返回一封邮件的完整信息，包括：
    ```json
    {
      "subject": "合同签署确认",
      "sender": "王五 <wangwu@example.com>",
      "date": "2023-10-17T11:20:00Z",
      "body": "请尽快完成合同签署...",
      "attachments": [
        {
          "filename": "合同.pdf",
          "size": 245678,
          "saved_path": "C:\\Temp\\合同.pdf"
        },
        ...
      ]
    }
    ```

---

### 5. `reply_to_email_by_number` 工具
- **Function Name**: `reply_to_email_by_number`
- **Description**: 对指定编号的邮件进行回复，并发送回复内容。
- **Parameters**:
  - `email_index`: 整数类型，表示邮件在最近一次列出的邮件列表中的索引位置（必填）。
  - `reply_content`: 字符串类型，表示回复内容（必填）。
- **Return Value**:
  - 返回一个字符串表示回复是否成功，例如：
    ```json
    "回复邮件已成功发送。"
    ```

---

### 6. `compose_email` 工具
- **Function Name**: `compose_email`
- **Description**: 新建并发送邮件，支持主题、正文、收件人和抄送。
- **Parameters**:
  - `subject`: 字符串类型，表示邮件主题（必填）。
  - `body`: 字符串类型，表示邮件正文（必填）。
  - `to`: 字符串类型，表示收件人邮箱地址（必填）。
  - `cc`: 字符串类型，表示抄送邮箱地址（可选）。
- **Return Value**:
  - 返回一个字符串表示邮件是否成功发送，例如：
    ```json
    "邮件已成功发送至 zhangsan@example.com。"
    ```

---

## Server Overview
该MCP服务器旨在通过JSON-RPC协议实现对本地Outlook客户端的自动化管理，提供列出文件夹、查看近期邮件、搜索邮件、读取邮件详情、回复邮件以及新建邮件等功能。所有功能均基于win32com库与Outlook交互，确保无需用户手动操作即可完成邮件相关任务。

---

## File to be Generated
- **File Name**: `mcp_outlook_server.py`

---

## Dependencies
- Python 3.10+
- `pywin32` (用于访问win32com接口)
- `mcp[cli]` (MCP SDK)