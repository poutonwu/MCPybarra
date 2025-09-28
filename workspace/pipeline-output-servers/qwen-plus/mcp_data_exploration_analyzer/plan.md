# MCP 服务器开发计划：自动化数据探索分析

## MCP 工具计划

### 1. `load_csv` 工具
- **描述**：加载 CSV 文件数据并将其存储在内存中，支持多个数据集同时操作。
- **参数**：
  - `file_path` (str)：CSV 文件的路径。
  - `dataset_name` (str)：用于标识该数据集的名称（可选，默认为文件名）。
- **返回值**：
  - 返回一个包含以下键的字典：
    - `"status"` (str)：操作状态（成功或失败）。
    - `"message"` (str)：操作结果的详细信息。
    - `"dataset_name"` (str)：已加载的数据集名称。

### 2. `run_script` 工具
- **描述**：执行用户提供的 Python 数据分析脚本，支持使用 pandas、numpy、scipy、sklearn 和 statsmodels 等数据分析库，并将处理结果保存到内存中供后续操作。
- **参数**：
  - `script_code` (str)：要执行的 Python 脚本代码。
  - `dataset_name` (str)：指定要使用的数据集名称。
- **返回值**：
  - 返回一个包含以下键的字典：
    - `"status"` (str)：操作状态（成功或失败）。
    - `"output"` (str)：脚本输出内容。
    - `"result_dataset_name"` (str)：处理后的数据集名称（如果有的话）。

### 3. `generate_exploration_plan` 工具
- **描述**：自动分析数据结构并生成数据探索计划，提供深度洞察的数据可视化建议。
- **参数**：
  - `dataset_name` (str)：需要进行探索的数据集名称。
- **返回值**：
  - 返回一个包含以下键的字典：
    - `"status"` (str)：操作状态（成功或失败）。
    - `"exploration_plan"` (dict)：包含数据结构分析和推荐的可视化方法。
    - `"visualization_suggestions"` (list)：推荐的图表类型列表（如直方图、散点图等）。

### 4. `execute_visualization` 工具
- **描述**：根据生成的数据探索计划执行数据可视化任务。
- **参数**：
  - `plan_id` (str)：指定要执行的探索计划 ID。
- **返回值**：
  - 返回一个包含以下键的字典：
    - `"status"` (str)：操作状态（成功或失败）。
    - `"visualization_result"` (str)：生成的图表数据（如 Base64 编码图像或 Vega-Lite JSON）。

## 服务器概述

本服务器旨在实现一个基于 MCP 协议的自动化数据探索分析系统。它能够加载 CSV 文件数据、执行 Python 数据分析脚本、生成数据探索计划并执行数据可视化任务。这些功能使得 AI 模型可以无缝地与数据分析工具集成，从而提供全面的数据分析能力。

## 需要生成的文件

- **文件名**：`mcp_data_analysis_server.py`
- **说明**：所有逻辑将包含在一个自包含的 Python 文件中，确保服务器可以直接运行而无需额外配置。

## 依赖项

- `mcp[cli]`：MCP SDK。
- `pandas`：用于数据处理和分析。
- `numpy`：用于数值计算。
- `scipy`：用于科学计算和统计分析。
- `scikit-learn` (`sklearn`)：用于机器学习算法。
- `statsmodels`：用于统计模型分析。
- `matplotlib` 或 `seaborn`：用于数据可视化。
- `httpx`：用于 HTTP 请求（如果需要外部 API）。