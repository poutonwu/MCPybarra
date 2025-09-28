# MCP 服务器开发计划：集成 OpenCV 的图像处理功能

## MCP Tools Plan

### 基础图像操作工具

#### `save_image_tool`
- **描述**: 保存图片文件
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `output_path` (str): 保存图像的目标路径
- **返回值**: 包含成功或失败消息的字符串

#### `resize_image_tool`
- **描述**: 调整图片尺寸
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `width` (int): 新宽度
  - `height` (int): 新高度
- **返回值**: 包含调整后的尺寸和保存路径的信息字符串

#### `crop_image_tool`
- **描述**: 裁剪图片区域
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `x` (int): 裁剪区域左上角 x 坐标
  - `y` (int): 裁剪区域左上角 y 坐标
  - `width` (int): 裁剪区域宽度
  - `height` (int): 裁剪区域高度
- **返回值**: 包含裁剪区域信息和保存路径的信息字符串

#### `get_image_stats_tool`
- **描述**: 获取图片统计信息
- **参数**:
  - `image_path` (str): 图像的文件路径
- **返回值**: 包含图像尺寸、颜色空间和像素值范围等信息的 JSON 字符串

### 高级图像处理工具

#### `apply_filter_tool`
- **描述**: 应用图像滤镜
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `filter_type` (str): 滤镜类型（例如 "gaussian", "median"）
  - `kernel_size` (int): 核大小
- **返回值**: 包含应用的滤镜类型和保存路径的信息字符串

#### `detect_edges_tool`
- **描述**: 检测图像边缘
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `method` (str): 边缘检测方法（例如 "canny"）
  - `threshold1` (int): 第一个阈值
  - `threshold2` (int): 第二个阈值
- **返回值**: 包含检测到的边缘数量和保存路径的信息字符串

#### `apply_threshold_tool`
- **描述**: 进行阈值分割
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `threshold_value` (int): 阈值
  - `max_value` (int): 最大值
- **返回值**: 包含应用的阈值和保存路径的信息字符串

#### `detect_contours_tool`
- **描述**: 检测图像轮廓
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `mode` (str): 轮廓检索模式（例如 "external", "tree"）
  - `method` (str): 轮廓近似方法（例如 "simple", "chain_approx_none"）
- **返回值**: 包含检测到的轮廓数量和保存路径的信息字符串

#### `find_shapes_tool`
- **描述**: 查找图像形状
- **参数**:
  - `image_path` (str): 图像的文件路径
  - `shape_type` (str): 形状类型（例如 "circle", "rectangle"）
- **返回值**: 包含找到的形状数量和位置信息的 JSON 字符段

## Server Overview
该 MCP 服务器将提供基本和高级图像处理功能，通过 Model Context Protocol (MCP) 集成 OpenCV。这将允许 AI 助手和语言模型访问强大的计算机视觉工具，用于从基本图像操作到高级对象检测和跟踪的各种任务。

## File to be Generated
所有代码将在单个 Python 文件中实现，命名为 `opencv_mcp_server.py`。

## Dependencies
- `mcp[cli]`: 用于构建 MCP 服务器
- `opencv-python`: 用于图像处理
- `httpx`: 用于 HTTP 请求