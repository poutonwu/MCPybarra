import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import traceback
import os
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("data_explorer")

# 用于存储加载的CSV数据集
loaded_datasets = {}

@mcp.tool()
def load_csv(dataset_name: str, file_path: str) -> str:
    """
    加载CSV文件到内存中。

    Args:
        dataset_name: 为加载的数据集指定一个名称。
        file_path: CSV文件的路径。

    Returns:
        一个字符串，表示加载成功或失败的消息。
    
    Raises:
        ValueError: 如果文件无法加载。
        FileNotFoundError: 如果指定的文件不存在。
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 将数据集存储在内存中
        loaded_datasets[dataset_name] = df
        
        return json.dumps({
            "status": "success",
            "message": f"成功加载数据集 '{dataset_name}' from '{file_path}'",
            "columns": list(df.columns),
            "rows": len(df)
        })
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到指定的文件: {file_path}")
    except Exception as e:
        raise ValueError(f"加载文件时发生错误: {str(e)}")

@mcp.tool()
def run_script(script_name: str, script_content: str) -> str:
    """
    执行Python数据分析脚本。

    Args:
        script_name: 脚本名称。
        script_content: 包含数据分析代码的字符串。

    Returns:
        一个字符串，表示脚本执行结果。
    
    Raises:
        ValueError: 如果脚本执行时发生错误。
    """
    try:
        # 创建一个字典来作为执行环境，包含所有支持的库和已加载的数据集
        exec_env = {
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'result': None,
            **loaded_datasets
        }
        
        # 执行脚本内容
        exec(script_content, exec_env)
        
        # 提取执行结果
        result = exec_env.get('result', 'No result variable found in script')
        
        # 返回结果
        return json.dumps({
            "status": "success",
            "script_name": script_name,
            "result": str(result)
        })
    except Exception as e:
        # 捕获异常并返回错误信息
        error_traceback = traceback.format_exc()
        raise ValueError(f"脚本执行错误: {str(e)}\n{error_traceback}")

@mcp.tool()
def explore_data(dataset_name: str, output_dir: str = "visualizations") -> str:
    """
    自动分析数据结构，生成数据探索计划并执行数据可视化。

    Args:
        dataset_name: 已加载数据集的名称。
        output_dir: 可视化图表的输出目录。

    Returns:
        一个字符串，表示探索和可视化结果。
    
    Raises:
        ValueError: 如果数据集不存在或处理时发生错误。
    """
    try:
        # 检查数据集是否存在
        if dataset_name not in loaded_datasets:
            raise ValueError(f"数据集 '{dataset_name}' 未加载")
        
        df = loaded_datasets[dataset_name]
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 基本数据统计
        summary = {
            "dataset_name": dataset_name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_info": {},
            "visualizations": []
        }
        
        # 分析每列数据
        for col in df.columns:
            col_type = "categorical" if df[col].dtype == "object" else "numerical"
            
            # 基本统计信息
            if col_type == "numerical":
                summary["column_info"][col] = {
                    "type": "numerical",
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std())
                }
                
                # 生成直方图
                plt.figure(figsize=(10, 6))
                df[col].hist(bins=50)
                plt.title(f"Distribution of {col}")
                plt.xlabel(col)
                plt.ylabel("Frequency")
                hist_path = os.path.join(output_dir, f"{col}_histogram.png")
                plt.savefig(hist_path)
                plt.close()
                summary["visualizations"].append(hist_path)
            else:
                summary["column_info"][col] = {
                    "type": "categorical",
                    "unique": int(df[col].nunique()),
                    "top": str(df[col].mode()[0]),
                    "count": int(df[col].value_counts().iloc[0])
                }
                
                # 生成条形图
                plt.figure(figsize=(12, 8))
                df[col].value_counts().head(10).plot(kind="bar")
                plt.title(f"Top 10 categories in {col}")
                plt.xlabel(col)
                plt.ylabel("Count")
                bar_path = os.path.join(output_dir, f"{col}_barchart.png")
                plt.savefig(bar_path)
                plt.close()
                summary["visualizations"].append(bar_path)
        
        # 生成相关性矩阵（如果所有列都是数值型）
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) >= 2:
            corr = df[numerical_cols].corr()
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr, annot=True, cmap="coolwarm")
            plt.title("Correlation Matrix")
            corr_path = os.path.join(output_dir, "correlation_matrix.png")
            plt.savefig(corr_path)
            plt.close()
            summary["visualizations"].append(corr_path)
        
        # 返回结果
        return json.dumps({
            "status": "success",
            "summary": summary
        })
    except Exception as e:
        # 捕获异常并返回错误信息
        error_traceback = traceback.format_exc()
        raise ValueError(f"数据探索错误: {str(e)}\n{error_traceback}")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        traceback.print_exc()