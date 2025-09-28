import sys
import os
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from mcp.server.fastmcp import FastMCP
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from io import StringIO
import traceback
import matplotlib.pyplot as plt
import base64
import re
from httpx import AsyncClient

# 设置代理（如果需要）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 初始化 FastMCP 服务器
mcp = FastMCP("mcp_data_exploration_analyzer")

# 存储加载的数据集和探索计划
data_store = {}
explanatory_plan_id_counter = 0

@mcp.tool()
async def load_csv(file_path: str, dataset_name: str = None) -> str:
    """
    加载 CSV 文件数据并将其存储在内存中，支持多个数据集同时操作。

    Args:
        file_path: CSV 文件的路径。
        dataset_name: 用于标识该数据集的名称（可选，默认为文件名）。

    Returns:
        一个包含状态、消息和数据集名称的 JSON 字符串。

    示例:
        load_csv(file_path="data.csv", dataset_name="my_dataset")
    """
    try:
        # 输入验证
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("'file_path' 不能为空。")
        
        if dataset_name is not None and (not isinstance(dataset_name, str) or not dataset_name.strip()):
            raise ValueError("'dataset_name' 必须是有效的字符串。")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 '{file_path}' 不存在。")
        
        if not file_path.lower().endswith('.csv'):
            raise ValueError("仅支持 CSV 文件格式。")
        
        # 如果 dataset_name 未提供，则使用文件名作为默认值
        if dataset_name is None:
            dataset_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 检查是否已经存在同名的数据集
        if dataset_name in data_store:
            raise ValueError(f"数据集 '{dataset_name}' 已经存在。")
        
        # 读取 CSV 文件
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            csv_data = f.read()
        
        # 使用 pandas 读取 CSV 数据
        df = pd.read_csv(StringIO(csv_data))
        
        # 存储数据集
        data_store[dataset_name] = {
            'data': df,
            'metadata': {
                'source_file': file_path,
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'column_types': dict(df.dtypes.astype(str)),
                'loaded_at': pd.Timestamp.now().isoformat()
            }
        }
        
        result = {
            "status": "success",
            "message": f"成功加载 {len(df)} 行数据到数据集 '{dataset_name}'",
            "dataset_name": dataset_name
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {
            "status": "error",
            "message": f"加载 CSV 时发生错误: {str(e)}",
            "traceback": error_traceback
        }
        return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def run_script(script_code: str, dataset_name: str) -> str:
    """
    执行用户提供的 Python 数据分析脚本，支持使用 pandas、numpy、scipy、sklearn 和 statsmodels 等数据分析库，并将处理结果保存到内存中供后续操作。

    Args:
        script_code: 要执行的 Python 脚本代码。
        dataset_name: 指定要使用的数据集名称。

    Returns:
        一个包含状态、脚本输出和处理后数据集名称的 JSON 字符串。

    示例:
        run_script(script_code="df.describe()", dataset_name="my_dataset")
    """
    try:
        # 输入验证
        if not isinstance(script_code, str) or not script_code.strip():
            raise ValueError("'script_code' 不能为空。")
        
        if not isinstance(dataset_name, str) or not dataset_name.strip():
            raise ValueError("'dataset_name' 必须是有效的字符串。")
        
        if dataset_name not in data_store:
            raise ValueError(f"数据集 '{dataset_name}' 不存在，请先使用 load_csv 加载数据。")
        
        # 获取原始数据集
        df = data_store[dataset_name]['data'].copy()
        
        # 创建一个字典来作为 exec 的命名空间
        namespace = {
            'pd': pd,
            'np': np,
            'sm': sm,
            'StandardScaler': StandardScaler,
            'PCA': PCA,
            'df': df,
            '__name__': '__main__',
            '__file__': 'run_script'
        }
        
        # 重定向标准输出
        import sys
        from io import StringIO
        stdout_capture = StringIO()
        sys.stdout = stdout_capture
        
        try:
            # 执行脚本
            compiled_code = compile(script_code, '<string>', 'exec')
            exec(compiled_code, namespace)
        finally:
            # 恢复标准输出
            sys.stdout = sys.__stdout__
        
        # 获取输出结果
        output = stdout_capture.getvalue()
        
        # 检查是否有新创建的数据帧
        new_df = namespace.get('result_df')
        result_dataset_name = None
        
        if new_df is not None and isinstance(new_df, pd.DataFrame):
            # 生成新的数据集名称
            result_dataset_name = f"{dataset_name}_processed_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
            
            # 存储处理后的数据集
            data_store[result_dataset_name] = {
                'data': new_df,
                'metadata': {
                    'source_dataset': dataset_name,
                    'script': script_code,
                    'output': output,
                    'num_rows': len(new_df),
                    'num_columns': len(new_df.columns),
                    'column_types': dict(new_df.dtypes.astype(str)),
                    'processed_at': pd.Timestamp.now().isoformat()
                }
            }
        
        result = {
            "status": "success",
            "output": output,
            "result_dataset_name": result_dataset_name
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {
            "status": "error",
            "message": f"执行脚本时发生错误: {str(e)}",
            "traceback": error_traceback
        }
        return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def generate_exploration_plan(dataset_name: str) -> str:
    """
    自动分析数据结构并生成数据探索计划，提供深度洞察的数据可视化建议。

    Args:
        dataset_name: 需要进行探索的数据集名称。

    Returns:
        一个包含状态、探索计划和可视化建议的 JSON 字符串。

    示例:
        generate_exploration_plan(dataset_name="my_dataset")
    """
    try:
        # 输入验证
        if not isinstance(dataset_name, str) or not dataset_name.strip():
            raise ValueError("'dataset_name' 必须是有效的字符串。")
        
        if dataset_name not in data_store:
            raise ValueError(f"数据集 '{dataset_name}' 不存在，请先使用 load_csv 加载数据。")
        
        # 获取数据集
        df = data_store[dataset_name]['data']
        
        # 分析数据结构
        analysis = {
            'basic_info': {
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'duplicates': int(df.duplicated().sum())
            },
            'column_analysis': {},
            'correlation_analysis': {},
            'missing_values': df.isnull().sum().to_dict(),
            'value_ranges': df.select_dtypes(include=[np.number]).agg(['min', 'max']).to_dict()
        }
        
        # 分析每列
        for col in df.columns:
            col_type = str(df[col].dtype)
            unique_count = df[col].nunique()
            null_count = df[col].isnull().sum()
            
            analysis['column_analysis'][col] = {
                'type': col_type,
                'unique_count': int(unique_count),
                'null_count': int(null_count),
                'sample_values': df[col].dropna().head(5).tolist()
            }
            
            # 如果是数值型列，计算基本统计信息
            if pd.api.types.is_numeric_dtype(df[col]):
                analysis['column_analysis'][col]['stats'] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'median': float(df[col].median()),
                    'quartiles': df[col].quantile([0.25, 0.5, 0.75]).tolist()
                }
        
        # 计算相关性矩阵（仅针对数值列）
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            correlation_matrix = df[numeric_cols].corr()
            analysis['correlation_analysis']['matrix'] = correlation_matrix.to_dict()
            
            # 找出最高相关的列对
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    if abs(correlation_matrix.iloc[i, j]) > 0.7:
                        high_correlations.append({
                            'columns': [correlation_matrix.columns[i], correlation_matrix.columns[j]],
                            'correlation': float(correlation_matrix.iloc[i, j])
                        })
            analysis['correlation_analysis']['high_correlations'] = high_correlations
        
        # 生成可视化建议
        visualization_suggestions = []
        
        # 对于每个数值列，建议直方图和箱线图
        for col in numeric_cols:
            visualization_suggestions.append(f"直方图 - {col} (分布)")
            visualization_suggestions.append(f"箱线图 - {col} (异常值检测)")
            
        # 对于类别型列，建议条形图
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            visualization_suggestions.append(f"条形图 - {col} (分布)")
            
        # 如果有至少两个数值列，建议散点图
        if len(numeric_cols) >= 2:
            # 取前几个高相关的列对
            top_pairs = analysis['correlation_analysis'].get('high_correlations', [])[:3]
            for pair in top_pairs:
                visualization_suggestions.append(f"散点图 - {pair['columns'][0]} vs {pair['columns'][1]} (相关性)")
            
        # 如果有时间序列数据，建议折线图
        datetime_cols = df.select_dtypes(include=['datetime']).columns
        if len(datetime_cols) > 0:
            visualization_suggestions.append("折线图 - 时间序列趋势")
            
        # 生成探索计划ID
        global explanatory_plan_id_counter
        explanatory_plan_id_counter += 1
        plan_id = f"exploration_plan_{explanatory_plan_id_counter:04d}"
        
        # 存储探索计划
        data_store[f"{dataset_name}_exploration_plan"] = {
            'plan_id': plan_id,
            'dataset_name': dataset_name,
            'analysis': analysis,
            'visualization_suggestions': visualization_suggestions,
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        result = {
            "status": "success",
            "exploration_plan": {
                "plan_id": plan_id,
                "analysis": analysis,
                "visualization_suggestions": visualization_suggestions
            }
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {
            "status": "error",
            "message": f"生成探索计划时发生错误: {str(e)}",
            "traceback": error_traceback
        }
        return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def execute_visualization(plan_id: str) -> str:
    """
    根据生成的数据探索计划执行数据可视化任务。

    Args:
        plan_id: 指定要执行的探索计划 ID。

    Returns:
        一个包含状态和可视化结果的 JSON 字符串。

    示例:
        execute_visualization(plan_id="exploration_plan_0001")
    """
    try:
        # 输入验证
        if not isinstance(plan_id, str) or not plan_id.strip():
            raise ValueError("'plan_id' 必须是有效的字符串。")
        
        # 查找对应的探索计划
        exploration_plan = None
        for key, value in data_store.items():
            if key.endswith('_exploration_plan') and value.get('plan_id') == plan_id:
                exploration_plan = value
                break
        
        if exploration_plan is None:
            raise ValueError(f"找不到 ID 为 '{plan_id}' 的探索计划。")
        
        # 获取关联的数据集
        dataset_name = exploration_plan['dataset_name']
        df = data_store[dataset_name]['data']
        
        # 执行可视化
        visualization_results = []
        
        # 为每个建议的可视化生成图表
        for idx, suggestion in enumerate(exploration_plan['visualization_suggestions'][:5]):  # 最多生成前5个图表
            try:
                # 解析建议
                match = re.match(r'(.*?)\s*-\s*(.*?)\s*$(.*?)$', suggestion)
                if not match:
                    continue
                
                chart_type = match.group(1).strip()
                column_info = match.group(2).strip()
                detail = match.group(3).strip()
                
                # 创建图表
                plt.figure(figsize=(10, 6))
                
                if chart_type == "直方图":
                    # 直方图
                    column = column_info
                    plt.hist(df[column].dropna(), bins=30, edgecolor='black')
                    plt.title(f"{column} 的分布")
                    plt.xlabel(column)
                    plt.ylabel("频率")
                    
                elif chart_type == "箱线图":
                    # 箱线图
                    column = column_info
                    plt.boxplot(df[column].dropna(), vert=False)
                    plt.title(f"{column} 的箱线图")
                    plt.xlabel(column)
                    
                elif chart_type == "条形图":
                    # 条形图
                    column = column_info
                    df[column].value_counts().plot(kind='bar', color='skyblue')
                    plt.title(f"{column} 的分布")
                    plt.xlabel(column)
                    plt.ylabel("数量")
                    
                elif chart_type == "散点图":
                    # 散点图
                    columns = [c.strip() for c in column_info.split('vs')]
                    if len(columns) == 2:
                        x_col, y_col = columns
                        plt.scatter(df[x_col], df[y_col], alpha=0.6)
                        plt.title(f"{x_col} vs {y_col}")
                        plt.xlabel(x_col)
                        plt.ylabel(y_col)
                        
                elif chart_type == "折线图":
                    # 折线图（假设有一个时间列）
                    time_col = None
                    for col in df.columns:
                        if pd.api.types.is_datetime64_dtype(df[col]):
                            time_col = col
                            break
                    if time_col:
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            y_col = numeric_cols[0]
                            plt.plot(df[time_col], df[y_col])
                            plt.title(f"{y_col} 随时间的变化")
                            plt.xlabel(time_col)
                            plt.ylabel(y_col)
                            plt.xticks(rotation=45)
                            
                else:
                    # 不支持的图表类型
                    continue
                
                # 将图表转换为 Base64 编码
                from io import BytesIO
                buf = BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format='png')
                plt.close()
                data_uri = base64.b64encode(buf.getvalue()).decode('utf-8')
                img_tag = f"data:image/png;base64,{data_uri}"
                
                visualization_results.append({
                    "chart_number": idx + 1,
                    "suggestion": suggestion,
                    "image": img_tag
                })
                
            except Exception as chart_error:
                visualization_results.append({
                    "chart_number": idx + 1,
                    "suggestion": suggestion,
                    "error": str(chart_error)
                })
                continue
        
        result = {
            "status": "success",
            "visualization_result": visualization_results
        }
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_traceback = traceback.format_exc()
        result = {
            "status": "error",
            "message": f"执行可视化时发生错误: {str(e)}",
            "traceback": error_traceback
        }
        return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()