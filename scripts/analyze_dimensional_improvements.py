#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析dimensional_scores_collection.csv中各框架相对于基线的五个维度提升情况
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# --- File & Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

INPUT_CSV = os.path.join(DATA_DIR, "dimensional_scores_collection.csv")
OUTPUT_IMPROVEMENTS_PNG = os.path.join(RESULTS_DIR, "dimensional_improvements.png")
OUTPUT_HEATMAP_PNG = os.path.join(RESULTS_DIR, "dimensional_improvements_heatmap.png")
OUTPUT_AVG_SCORES_CSV = os.path.join(DATA_DIR, "dimensional_average_scores.csv")
OUTPUT_IMPROVEMENTS_CSV = os.path.join(DATA_DIR, "dimensional_improvements.csv")

def load_data(file_path):
    """加载CSV数据"""
    df = pd.read_csv(file_path)
    return df

def extract_dimensions(df):
    """提取五个维度的数据"""
    dimensions = ['Functionality', 'Performance', 'Robustness', 'Security', 'Transparency']
    
    # 获取所有列名
    columns = df.columns.tolist()[1:]  # 排除第一列（Test Subject）
    
    # 按维度分组
    dimension_columns = defaultdict(list)
    for col in columns:
        for dim in dimensions:
            if f":{dim}" in col:
                dimension_columns[dim].append(col)
    
    return dimension_columns

def calculate_average_by_model(df, dimension_columns):
    """计算每个模型在每个维度上的平均分数，排除得分为零的项目"""
    models = {
        "Public Baseline": "Public Baseline-ave",
        "MCPybarra-gemini": "gemini-2.5-pro-ave",
        "MCPybarra-gpt4o": "gpt-4o-ave",
        "MCPybarra-qwen-max": "qwen-max-ave",
        "MCPybarra-qwen-max-latest": "qwen-max-latest-ave",
        "MCPybarra-qwen-plus": "qwen-plus-ave",
        "MetaGPT": "metaGPT-qwen-plus-ave"
    }
    
    results = {}
    
    for model_name, model_row in models.items():
        model_data = df[df['Test Subject'] == model_row]
        
        if len(model_data) == 0:
            print(f"警告: 未找到模型 {model_row}")
            continue
        
        model_results = {}
        
        for dim, cols in dimension_columns.items():
            # 获取该维度下所有列的值，并将0替换为np.nan
            values = []
            for col in cols:
                if col in model_data.columns:
                    val = model_data[col].values[0]
                    if not np.isnan(val):
                        # 将0替换为np.nan，这样在计算平均值时会被自动忽略
                        values.append(np.nan if val == 0 else val)
            
            # 使用np.nanmean计算平均值，自动忽略np.nan
            if values:
                model_results[dim] = np.nanmean(values)
            else:
                model_results[dim] = 0
        
        results[model_name] = model_results
    
    return results

def calculate_improvements(baseline_scores, model_scores):
    """计算相对于基线的提升"""
    improvements = {}
    
    for model_name, model_data in model_scores.items():
        if model_name == "Public Baseline":
            continue
        
        model_improvements = {}
        for dim, score in model_data.items():
            baseline_score = baseline_scores[dim]
            improvement = score - baseline_score
            model_improvements[dim] = improvement
        
        improvements[model_name] = model_improvements
    
    return improvements

def print_results(average_scores, improvements):
    """打印结果"""
    print("\n基线平均分:")
    for dim, score in average_scores["Public Baseline"].items():
        print(f"{dim}: {score:.2f}")
    
    print("\n各模型在各维度上的平均分:")
    for model, scores in average_scores.items():
        if model == "Public Baseline":
            continue
        print(f"\n{model}:")
        for dim, score in scores.items():
            print(f"{dim}: {score:.2f}")
    
    print("\n各模型相对于基线的提升:")
    for model, impr in improvements.items():
        print(f"\n{model}:")
        for dim, val in impr.items():
            print(f"{dim}: {val:+.2f}")

def plot_improvements(improvements):
    """绘制提升图表"""
    # 准备数据
    models = list(improvements.keys())
    dimensions = list(improvements[models[0]].keys())
    
    data = []
    for model in models:
        for dim in dimensions:
            data.append({
                "模型": model,
                "维度": dim,
                "提升": improvements[model][dim]
            })
    
    df = pd.DataFrame(data)
    
    # 绘制图表
    plt.figure(figsize=(14, 8))
    sns.barplot(x="维度", y="提升", hue="模型", data=df)
    plt.title("各模型在五个维度上相对于基线的提升", fontsize=16)
    plt.xlabel("维度", fontsize=14)
    plt.ylabel("提升分数", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title="模型", fontsize=12, title_fontsize=13)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 保存图表
    plt.tight_layout()
    plt.savefig(OUTPUT_IMPROVEMENTS_PNG, dpi=300)
    plt.close()

def create_heatmap(improvements):
    """创建热力图"""
    # 准备数据
    models = list(improvements.keys())
    dimensions = list(improvements[models[0]].keys())
    
    data = np.zeros((len(models), len(dimensions)))
    for i, model in enumerate(models):
        for j, dim in enumerate(dimensions):
            data[i, j] = improvements[model][dim]
    
    # 绘制热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(data, annot=True, fmt=".2f", cmap="RdYlGn", 
                xticklabels=dimensions, yticklabels=models)
    plt.title("各模型在五个维度上相对于基线的提升热力图", fontsize=16)
    plt.xlabel("维度", fontsize=14)
    plt.ylabel("模型", fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_HEATMAP_PNG, dpi=300)
    plt.close()

def export_to_csv(average_scores, improvements):
    """导出结果到CSV文件"""
    # 导出平均分
    avg_data = []
    for model, scores in average_scores.items():
        row = {"模型": model}
        for dim, score in scores.items():
            row[dim] = score
        avg_data.append(row)
    
    avg_df = pd.DataFrame(avg_data)
    avg_df.to_csv(OUTPUT_AVG_SCORES_CSV, index=False)
    
    # 导出提升数据
    imp_data = []
    for model, impr in improvements.items():
        row = {"模型": model}
        for dim, val in impr.items():
            row[dim] = val
        imp_data.append(row)
    
    imp_df = pd.DataFrame(imp_data)
    imp_df.to_csv(OUTPUT_IMPROVEMENTS_CSV, index=False)

def main():
    """主函数"""
    # 加载数据
    if not os.path.exists(INPUT_CSV):
        print(f"错误: 文件 {INPUT_CSV} 不存在")
        return
    
    df = load_data(INPUT_CSV)
    
    # 提取维度列
    dimension_columns = extract_dimensions(df)
    
    # 计算每个模型在每个维度的平均分
    average_scores = calculate_average_by_model(df, dimension_columns)
    
    # 计算相对于基线的提升
    baseline_scores = average_scores["Public Baseline"]
    improvements = calculate_improvements(baseline_scores, average_scores)
    
    # 打印结果
    print_results(average_scores, improvements)
    
    # 导出结果到CSV
    export_to_csv(average_scores, improvements)
    
    # 绘制图表
    plot_improvements(improvements)
    create_heatmap(improvements)
    
    print("\n分析完成! 结果已保存到CSV文件和图表中。")

if __name__ == "__main__":
    main()