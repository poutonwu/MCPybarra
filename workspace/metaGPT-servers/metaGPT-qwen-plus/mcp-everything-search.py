import sys
import ctypes
import os
import re
import fnmatch
import stat
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from mcp.server.fastmcp import FastMCP

# 初始化FastMCP服务器
mcp = FastMCP("everything_search")

# 加载Everything SDK DLL
try:
    everything_dll_path = "D:\devEnvironment\Everything\dll\Everything64.dll"
    if not os.path.exists(everything_dll_path):
        everything_dll_path = "D:\devEnvironment\Everything\dll\Everything64.dll"
    
    if os.path.exists(everything_dll_path):
        everything = ctypes.CDLL(everything_dll_path)
    else:
        raise FileNotFoundError("Everything DLL not found. Please install Everything SDK.")
except Exception as e:
    print(f"Error loading Everything DLL: {e}")
    raise

# 定义Everything SDK常量和结构体
EVERYTHING_IPC = ctypes.c_int(0x57BCD)
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100
EVERYTHING_REQUEST_FILE_LIST_FILE_NAME = 0x00000200
EVERYTHING_REQUEST_RUN_COUNT = 0x00000400
EVERYTHING_REQUEST_TITLE = 0x00000800
EVERYTHING_REQUEST_AUTHOR = 0x00001000
EVERYTHING_REQUEST_KEYWORD = 0x00002000

EVERYTHING_SORT_NAME_ASCENDING = 1
EVERYTHING_SORT_PATH_ASCENDING = 2
EVERYTHING_SORT_SIZE_ASCENDING = 3
EVERYTHING_SORT_DATE_MODIFIED_ASCENDING = 4
EVERYTHING_SORT_TYPE_ASCENDING = 5
EVERYTHING_SORT_NAME_DESCENDING = 6
EVERYTHING_SORT_PATH_DESCENDING = 7
EVERYTHING_SORT_SIZE_DESCENDING = 8
EVERYTHING_SORT_DATE_MODIFIED_DESCENDING = 9
EVERYTHING_SORT_TYPE_DESCENDING = 10

class EverythingResult(ctypes.Structure):
    _fields_ = [
        ("file_name", ctypes.c_wchar_p),
        ("path", ctypes.c_wchar_p),
        ("full_path_and_file_name", ctypes.c_wchar_p),
        ("extension", ctypes.c_wchar_p),
        ("size", ctypes.c_ulonglong),
        ("date_created", ctypes.c_ulonglong),
        ("date_modified", ctypes.c_ulonglong),
        ("date_accessed", ctypes.c_ulonglong),
        ("attributes", ctypes.c_ulong),
        ("file_list_file_name", ctypes.c_wchar_p),
        ("run_count", ctypes.c_ulong),
        ("title", ctypes.c_wchar_p),
        ("author", ctypes.c_wchar_p),
        ("keyword", ctypes.c_wchar_p),
    ]

# 配置Everything SDK函数原型
everything.Everything_SetRequestFlags.argtypes = [ctypes.c_ulong]
everything.Everything_SetRequestFlags.restype = None

everything.Everything_SetSort.argtypes = [ctypes.c_int]
everything.Everything_SetSort.restype = None

everything.Everything_QueryW.argtypes = [ctypes.c_bool]
everything.Everything_QueryW.restype = ctypes.c_bool

everything.Everything_GetNumResults.argtypes = []
everything.Everything_GetNumResults.restype = ctypes.c_ulong

everything.Everything_GetResultStruct.argtypes = [ctypes.c_ulong, ctypes.POINTER(EverythingResult)]
everything.Everything_GetResultStruct.restype = None

def convert_file_size(size_bytes: int) -> str:
    """将字节大小转换为可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f}TB"

def format_datetime(timestamp: int) -> str:
    """将Windows文件时间戳转换为可读格式"""
    try:
        # Windows FILETIME to Unix timestamp
        unix_time = (timestamp - 116444736000000000) // 10000000
        return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "N/A"

def get_file_attributes_info(attributes: int) -> Dict[str, bool]:
    """解析文件属性标志"""
    return {
        "read_only": bool(attributes & stat.FILE_ATTRIBUTE_READONLY),
        "hidden": bool(attributes & stat.FILE_ATTRIBUTE_HIDDEN),
        "system": bool(attributes & stat.FILE_ATTRIBUTE_SYSTEM),
        "directory": bool(attributes & stat.FILE_ATTRIBUTE_DIRECTORY),
        "archive": bool(attributes & stat.FILE_ATTRIBUTE_ARCHIVE),
        "device": bool(attributes & stat.FILE_ATTRIBUTE_DEVICE),
        "normal": bool(attributes & stat.FILE_ATTRIBUTE_NORMAL),
        "temporary": bool(attributes & stat.FILE_ATTRIBUTE_TEMPORARY),
        "sparse_file": bool(attributes & stat.FILE_ATTRIBUTE_SPARSE_FILE),
        "reparse_point": bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT),
        "compressed": bool(attributes & stat.FILE_ATTRIBUTE_COMPRESSED),
        "offline": bool(attributes & stat.FILE_ATTRIBUTE_OFFLINE),
        "not_content_indexed": bool(attributes & stat.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED),
        "encrypted": bool(attributes & stat.FILE_ATTRIBUTE_ENCRYPTED)
    }

@mcp.tool()
async def search_files(
    query: str,
    max_results: int = 100,
    sort_by: str = "name_asc",
    case_sensitive: bool = False,
    whole_word: bool = False,
    regex_match: bool = False,
    limit_to_files: bool = False,
    limit_to_folders: bool = False,
    path_filter: Optional[str] = None,
    size_min: Optional[int] = None,
    size_max: Optional[int] = None,
    date_modified_min: Optional[str] = None,
    date_modified_max: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用Everything SDK执行高级文件搜索
    
    Args:
        query: 搜索查询字符串（支持通配符、正则表达式等）
        max_results: 最大返回结果数（默认100，最大1000）
        sort_by: 排序方式（name_asc, name_desc, path_asc, path_desc, 
                size_asc, size_desc, date_asc, date_desc）
        case_sensitive: 是否区分大小写
        whole_word: 是否全词匹配
        regex_match: 是否使用正则表达式匹配
        limit_to_files: 仅搜索文件（排除文件夹）
        limit_to_folders: 仅搜索文件夹（排除文件）
        path_filter: 路径过滤器（例如：C:\\Users\$$\\My Documents））
        size_min: 最小文件大小（字节）
        size_max: 最大文件大小（字节）
        date_modified_min: 最小修改日期（ISO格式字符串）
        date_modified_max: 最大修改日期（ISO格式字符串）
        
    Returns:
        包含搜索结果和元数据的字典：
        {
            "results": List[Dict],  # 文件信息列表
            "total_results": int,   # 总结果数
            "query_time_ms": int,   # 查询耗时（毫秒）
            "used_regex": bool      # 是否实际使用了正则表达式
        }
        
    Raises:
        ValueError: 如果参数验证失败
        RuntimeError: 如果搜索过程中发生错误
        
    示例:
        search_files(query="*.txt", sort_by="size_desc", limit_to_files=True)
    """
    # 参数验证
    if not query or not isinstance(query, str):
        raise ValueError("查询字符串不能为空")
        
    if max_results < 1 or max_results > 1000:
        raise ValueError("max_results必须在1-1000之间")
        
    # 设置请求标志
    request_flags = (
        EVERYTHING_REQUEST_FILE_NAME |
        EVERYTHING_REQUEST_PATH |
        EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME |
        EVERYTHING_REQUEST_EXTENSION |
        EVERYTHING_REQUEST_SIZE |
        EVERYTHING_REQUEST_DATE_MODIFIED |
        EVERYTHING_REQUEST_ATTRIBUTES
    )
    everything.Everything_SetRequestFlags(request_flags)
    
    # 设置排序方式
    sort_map = {
        "name_asc": EVERYTHING_SORT_NAME_ASCENDING,
        "name_desc": EVERYTHING_SORT_NAME_DESCENDING,
        "path_asc": EVERYTHING_SORT_PATH_ASCENDING,
        "path_desc": EVERYTHING_SORT_PATH_DESCENDING,
        "size_asc": EVERYTHING_SORT_SIZE_ASCENDING,
        "size_desc": EVERYTHING_SORT_SIZE_DESCENDING,
        "date_asc": EVERYTHING_SORT_DATE_MODIFIED_ASCENDING,
        "date_desc": EVERYTHING_SORT_DATE_MODIFIED_DESCENDING
    }
    
    if sort_by not in sort_map:
        raise ValueError(f"不支持的排序方式: {sort_by}. 支持的方式: {list(sort_map.keys())}")
        
    everything.Everything_SetSort(sort_map[sort_by])
    
    # 构建查询字符串
    final_query = ""
    
    # 处理路径过滤
    if path_filter:
        final_query += f'"{path_filter}" '
        
    # 添加主查询
    if regex_match:
        final_query += query  # 直接使用正则表达式
    elif whole_word:
        final_query += f'"{query}"'  # 全词匹配
    else:
        final_query += query
        
    # 处理文件/文件夹过滤
    if limit_to_files and limit_to_folders:
        raise ValueError("不能同时限制为文件和文件夹")
        
    if limit_to_files:
        final_query += " type:file"
        
    if limit_to_folders:
        final_query += " type:folder"
        
    # 处理大小过滤
    if size_min is not None:
        final_query += f" size:>{size_min}"
        
    if size_max is not None:
        final_query += f" size:<{size_max}"
        
    # 处理日期范围过滤
    if date_modified_min:
        try:
            dt = datetime.fromisoformat(date_modified_min)
            final_query += f' date-modified:>"{dt.strftime("%Y-%m-%d")}"'
        except ValueError:
            raise ValueError(f"无效的最小日期格式: {date_modified_min}. 应使用ISO格式(YYYY-MM-DD)")
            
    if date_modified_max:
        try:
            dt = datetime.fromisoformat(date_modified_max)
            final_query += f' date-modified:<"{dt.strftime("%Y-%m-%d")}"'
        except ValueError:
            raise ValueError(f"无效的最大日期格式: {date_modified_max}. 应使用ISO格式(YYYY-MM-DD)")
            
    # 执行查询
    everything.Everything_SetSearchW(final_query)
    start_time = datetime.now()
    success = everything.Everything_QueryW(True)
    end_time = datetime.now()
    
    if not success:
        error_code = everything.Everything_GetLastError()
        raise RuntimeError(f"Everything查询失败，错误代码: {error_code}")
        
    # 获取结果
    result_count = everything.Everything_GetNumResults()
    results = []
    
    for i in range(min(result_count, max_results)):
        result = EverythingResult()
        everything.Everything_GetResultStruct(i, ctypes.byref(result))
        
        file_info = {
            "file_name": result.file_name,
            "path": result.path,
            "full_path": result.full_path_and_file_name,
            "extension": result.extension,
            "size": result.size,
            "size_readable": convert_file_size(result.size),
            "date_modified": format_datetime(result.date_modified),
            "attributes": get_file_attributes_info(result.attributes)
        }
        
        # 应用额外的过滤条件（如果启用）
        match = True
        
        # 如果启用了正则匹配，在这里进行最终验证
        if regex_match:
            try:
                if not re.search(query, file_info["full_path"], flags=re.IGNORECASE if not case_sensitive else 0):
                    match = False
            except re.error as e:
                raise ValueError(f"正则表达式无效: {str(e)}")
                
        # 常规匹配
        elif not regex_match and not whole_word and not case_sensitive:
            if query.lower() not in file_info["full_path"].lower():
                match = False
                
        elif not regex_match and not whole_word and case_sensitive:
            if query not in file_info["full_path"]:
                match = False
                
        elif not regex_match and whole_word and case_sensitive:
            if query not in file_info["full_path"].split():
                match = False
                
        elif not regex_match and whole_word and not case_sensitive:
            if query.lower() not in file_info["full_path"].lower().split():
                match = False
                
        if match:
            results.append(file_info)
    
    return {
        "results": results,
        "total_results": result_count,
        "query_time_ms": int((end_time - start_time).total_seconds() * 1000),
        "used_regex": regex_match
    }

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()