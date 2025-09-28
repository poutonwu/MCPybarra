#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import glob
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入相关模块
from testSystem.reporting import SCORE_DIMENSIONS, SCORE_WEIGHTS, DIMENSION_MAP_EN

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def _simplify_public_name(name: str) -> str:
    """Simplifies the public server name for better readability on charts using a specific mapping."""
    name = name.lower()
    # This explicit mapping is more robust than generic string replacement.
    mapping = {
        "academic-search-mcp-server-master": "academic search",
        "arxiv-mcp-server-main": "arxiv",
        "duckduckgo-mcp-server-main": "duckduckgo",
        "flights-mcp-main": "flights",
        "huggingface-mcp-server-main": "huggingface",
        "image-file-converter-mcp-server-main": "image converter",
        "markitdown-main": "markdown",
        "mcp-doc-main": "word automation (doc)",
        "office-word-mcp-server-main": "word processor (office)",
        "mcp-everything-search-main": "everything search",
        "mcp-official-git": "git",
        "mcp-pdf-tools": "pdf tools",
        "mcp-server-data-exploration-main": "data exploration",
        "mcp-server-main": "financial data",
        "mcp-tavily-main": "tavily",
        "mcp-text-editor-main": "text editor",
        "mcp_search_images-main": "image search",
        "mongo-mcp-main": "mongodb",
        "my-mcp-ssh-master": "ssh",
        "mysql_mcp_server-main": "mysql",
        "opencv-mcp-server-main": "opencv",
        "outlook-mcp-server-main": "outlook",
        "screenshot-server-main": "screenshot",
        "unsplash-mcp-server-main": "unsplash",
        "zotero-mcp-main": "zotero",
    }
    return mapping.get(name, name).title()

def extract_model_name_from_report(report_name: str) -> str:
    """从报告名称中提取模型名称"""
    model_patterns = ['gpt-4o', 'qwen-plus', 'gemini-2.5-pro']
    for model in model_patterns:
        if model in report_name:
            return model
    return "unknown"

def extract_project_name_from_report(report_name: str, model_name: str) -> str:
    """从报告名称中提取项目名称"""
    if model_name != "unknown":
        return report_name.replace(f"{model_name}-", "", 1)
    return report_name

def extract_scores_from_md(md_file: str) -> Dict:
    """从MD文件中提取得分信息"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scores_pattern = r'<SCORES>(.*?)</SCORES>'
        scores_match = re.search(scores_pattern, content, re.DOTALL)
        
        dimension_scores = {dim: 0 for dim in SCORE_DIMENSIONS}
        total_score = 0
        
        if scores_match:
            scores_text = scores_match.group(1).strip()
            for line in scores_text.split('\n'):
                # 提取各维度得分
                for dimension, weight in SCORE_WEIGHTS.items():
                    if line.startswith(dimension) or line.startswith(DIMENSION_MAP_EN[dimension]):
                        match = re.search(r'(\d+)/' + str(weight), line)
                        if match:
                            dimension_scores[dimension] = int(match.group(1))
                
                # 提取总分
                if line.startswith("总分") or line.startswith("Total Score"):
                    match = re.search(r'(\d+)/100', line)
                    if match:
                        total_score = int(match.group(1))
        
        if total_score == 0:
            total_score = sum(dimension_scores.values())
        
        return {
            "scores": dimension_scores,
            "total_score": total_score
        }
    except Exception as e:
        print(f"从文件 {md_file} 提取得分时出错: {str(e)}")
        return {
            "scores": {dim: 0 for dim in SCORE_DIMENSIONS},
            "total_score": 0
        }

def extract_llm_usage_from_md(md_file: str) -> Dict:
    """从MD文件中提取LLM使用情况"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试提取token使用量
        token_match = re.search(r'总Token使用量：(\d+)', content)
        if token_match:
            tokens = int(token_match.group(1))
            return {"total_tokens": tokens}
        
        # 尝试提取英文token使用量
        token_match_en = re.search(r'Total Tokens Used: (\d+)', content)
        if token_match_en:
            tokens = int(token_match_en.group(1))
            return {"total_tokens": tokens}
    except Exception as e:
        print(f"提取LLM使用情况时出错: {str(e)}")
    
    return {"total_tokens": 0}

def extract_duration_from_md(md_file: str) -> float:
    """从MD文件中提取执行时间"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试提取执行时间
        duration_match = re.search(r'总执行时间：(\d+\.\d+)秒', content)
        if duration_match:
            return float(duration_match.group(1))
        
        # 尝试提取英文执行时间
        duration_match_en = re.search(r'Total Execution Time: (\d+\.\d+) seconds', content)
        if duration_match_en:
            return float(duration_match_en.group(1))
    except Exception as e:
        print(f"提取执行时间时出错: {str(e)}")
    
    return 0.0

def load_reports_from_md(base_dir: str) -> Tuple[Dict, Dict]:
    """从MD文件中加载报告信息"""
    all_reports = {}
    report_to_model_map = {}
    
    # 加载 pipeline_mapping.json
    mapping_file = os.path.abspath(os.path.join(base_dir, '..', '..', 'workspace', 'pipeline_mapping.json'))
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            pipeline_mapping = json.load(f)
    except FileNotFoundError:
        print(f"错误: 映射文件未找到 at {mapping_file}")
        return {}, {}
    
    # 创建 (model, project_name) -> public_server_name 的反向映射
    reverse_mapping = {}
    for item in pipeline_mapping:
        public_name = item.get("public_server_name")
        if not public_name:
            continue
        for model, details in item.get("generated_servers", {}).items():
            if details and "project_name" in details:
                reverse_mapping[(model, details["project_name"])] = public_name

    # 遍历所有模型目录
    model_dirs = [d for d in os.listdir(os.path.join(base_dir, "pipeline_server_tests")) 
                 if os.path.isdir(os.path.join(base_dir, "pipeline_server_tests", d))]
    
    for model_dir in model_dirs:
        model_path = os.path.join(base_dir, "pipeline_server_tests", model_dir)
        
        # 查找所有详细报告MD文件
        detailed_report_files = glob.glob(os.path.join(model_path, "detailed_report_*.md"))
        
        for report_file in detailed_report_files:
            try:
                # 提取报告名称
                report_name_full = os.path.basename(report_file).replace("detailed_report_", "").replace(".md", "")
                
                # 提取模型名称
                model_name = extract_model_name_from_report(report_name_full)
                
                # 提取项目名称
                project_name = extract_project_name_from_report(report_name_full, model_name)
                
                # 使用反向映射查找 public_server_name
                public_server_name = reverse_mapping.get((model_name, project_name))

                if not public_server_name:
                    print(f"警告: 在 pipeline_mapping.json 中找不到匹配项: model='{model_name}', project='{project_name}'，已跳过此报告。")
                    continue
                else:
                    simplified_name = _simplify_public_name(public_server_name)

                # 提取得分
                scores = extract_scores_from_md(report_file)
                
                # 提取LLM使用情况
                llm_usage = extract_llm_usage_from_md(report_file)
                
                # 提取执行时间
                duration = extract_duration_from_md(report_file)
                
                # 创建报告数据结构
                report_data = {
                    "report_name": report_name_full,
                    "model": model_name,
                    "project": project_name,
                    "simplified_name": simplified_name,
                    "scores": scores["scores"],
                    "total_score": scores["total_score"],
                    "total_tokens": llm_usage["total_tokens"],
                    "duration": duration
                }
                
                # 添加到结果字典
                all_reports[report_name_full] = report_data
                report_to_model_map[report_name_full] = model_name
                
                print(f"已加载报告: {report_name_full} | 简化名称: {simplified_name} | 得分: {scores['total_score']}")
            except Exception as e:
                print(f"处理报告 {report_file} 时出错: {str(e)}")
    
    return all_reports, report_to_model_map

def create_pipeline_mapping(all_reports: Dict) -> List[Dict]:
    """创建pipeline映射"""
    pipeline_mapping = []
    
    # 按简化项目名称分组
    projects = {}
    for report_name, report_data in all_reports.items():
        simplified_name = report_data["simplified_name"]
        model_name = report_data["model"]
        
        # 添加到项目字典
        if simplified_name not in projects:
            projects[simplified_name] = {"public_server": simplified_name, "generated_servers": {}}
        
        # 添加生成的服务器信息
        projects[simplified_name]["generated_servers"][model_name] = {
            "server_path": "",  # 没有实际路径信息
            "project_name": report_name
        }
    
    # 转换为列表
    for project_name, project_data in projects.items():
        pipeline_mapping.append(project_data)
    
    return pipeline_mapping

def generate_pipeline_comparison_report(all_reports: Dict, report_to_model_map: Dict, output_dir: str):
    """生成pipeline比较报告"""
    print("\n====== 生成Pipeline比较报告 ======")
    
    # 按简化项目名称分组
    projects_by_name = {}
    for report_name, report_data in all_reports.items():
        simplified_name = report_data["simplified_name"]
        
        if simplified_name not in projects_by_name:
            projects_by_name[simplified_name] = {}
        
        model_name = report_data["model"]
        projects_by_name[simplified_name][model_name] = report_data
    
    # 创建比较表格
    models = ["gemini-2.5-pro", "gpt-4o", "qwen-plus"]
    
    # 总分比较表格
    score_table = {"public_server_name": []}
    for model in models:
        score_table[model] = []
    
    # 执行时间比较表格
    duration_table = {"public_server_name": []}
    for model in models:
        duration_table[model] = []
    
    # Token使用比较表格
    token_table = {"public_server_name": []}
    for model in models:
        token_table[model] = []
    
    # 填充表格数据
    for project_name, project_data in projects_by_name.items():
        score_table["public_server_name"].append(project_name)
        duration_table["public_server_name"].append(project_name)
        token_table["public_server_name"].append(project_name)
        
        for model in models:
            if model in project_data:
                score_table[model].append(project_data[model]["total_score"])
                duration_table[model].append(project_data[model]["duration"])
                token_table[model].append(project_data[model]["total_tokens"])
            else:
                score_table[model].append(0)
                duration_table[model].append(0)
                token_table[model].append(0)
    
    # 计算平均分
    score_table["public_server_name"].append("Average Score")
    for model in models:
        scores = [s for s in score_table[model] if s and s > 0]
        avg_score = sum(scores) / len(scores) if scores else 0
        score_table[model].append(round(avg_score, 2))
    
    # 计算总执行时间
    duration_table["public_server_name"].append("Total Duration")
    for model in models:
        total_duration = sum(duration_table[model])
        duration_table[model].append(total_duration)
    
    # 计算总Token使用量
    token_table["public_server_name"].append("Total Tokens")
    for model in models:
        total_tokens = sum(token_table[model])
        token_table[model].append(total_tokens)
    
    # 创建DataFrame
    score_df = pd.DataFrame(score_table)
    duration_df = pd.DataFrame(duration_table)
    token_df = pd.DataFrame(token_table)
    
    # 生成Markdown报告
    report = "# Pipeline Model Performance Comparison Report\n\n"
    report += "This report compares the performance of different AI models on the same server generation tasks.\n\n"
    
    # 添加总分比较表格
    report += "## 1. Overall Score Comparison (Higher is Better)\n\n"
    report += score_df.to_markdown(index=False) + "\n\n"
    
    # 添加执行时间比较表格
    report += "## 2. Total Duration Comparison (in seconds, Lower is Better)\n\n"
    report += duration_df.to_markdown(index=False) + "\n\n"
    
    # 添加Token使用比较表格
    report += "## 3. Total Token Consumption (Lower is Better)\n\n"
    report += token_df.to_markdown(index=False) + "\n\n"
    
    # 保存报告
    report_file = os.path.join(output_dir, "pipeline_comparison_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Pipeline比较报告已保存到: {report_file}")
    
    # 生成可视化图表
    generate_pipeline_comparison_chart(score_df, output_dir)

def generate_pipeline_comparison_chart(score_df: pd.DataFrame, output_dir: str):
    """生成pipeline比较图表"""
    # 移除平均分行
    chart_df = score_df[score_df["public_server_name"] != "Average Score"].copy()
    
    # 准备数据
    project_names = chart_df["public_server_name"].tolist()
    models = ["gemini-2.5-pro", "gpt-4o", "qwen-plus"]
    
    # 设置图表大小和样式
    plt.figure(figsize=(20, 10))
    
    # 设置柱状图位置
    x = np.arange(len(project_names))
    width = 0.25
    
    # 绘制柱状图
    colors = ['#673AB7', '#2196F3', '#4CAF50']  # 紫色、蓝色、绿色
    
    for i, model in enumerate(models):
        plt.bar(x + (i - 1) * width, chart_df[model], width, label=model, color=colors[i])
    
    # 添加标题和标签
    plt.title('Pipeline Model Performance Comparison (Overall Score)', fontsize=16)
    plt.xlabel('Project', fontsize=12)
    plt.ylabel('Total Score', fontsize=12)
    
    # 设置x轴刻度
    plt.xticks(x, project_names, rotation=45, ha='right')
    
    # 设置y轴范围
    plt.ylim(0, 105)
    
    # 添加网格线
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 在每个柱子上添加得分标签
    for i, model in enumerate(models):
        for j, score in enumerate(chart_df[model]):
            if score > 0:  # 只显示非零得分
                plt.text(j + (i - 1) * width, score + 1, str(score), 
                        ha='center', va='bottom', fontsize=8)
    
    # 添加图例
    plt.legend(title='Model', loc='upper right')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    chart_file = os.path.join(output_dir, "pipeline_comparison_scores.png")
    plt.savefig(chart_file, dpi=300)
    plt.close()
    
    print(f"Pipeline比较图表已保存到: {chart_file}")

def generate_benchmark_summary(all_reports: Dict, report_to_model_map: Dict, output_dir: str):
    """生成benchmark摘要"""
    print("\n====== 生成Benchmark摘要 ======")
    
    # 按模型分组
    reports_by_model = {}
    for report_name, report_data in all_reports.items():
        model_name = report_data["model"]
        
        if model_name not in reports_by_model:
            reports_by_model[model_name] = []
        
        reports_by_model[model_name].append(report_data)
    
    # 计算每个模型的统计数据
    summary = {}
    for model, reports in reports_by_model.items():
        # 计算平均分，忽略0分
        valid_scores = [r["total_score"] for r in reports if r["total_score"] > 0]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        # 计算各维度平均分，忽略0分
        dimension_scores = {dim: 0 for dim in SCORE_DIMENSIONS}
        for dim in SCORE_DIMENSIONS:
            dim_scores = [r["scores"][dim] for r in reports if r["scores"][dim] > 0]
            dimension_scores[dim] = sum(dim_scores) / len(dim_scores) if dim_scores else 0
        
        # 计算总Token使用量
        total_tokens = sum(r["total_tokens"] for r in reports)
        
        # 计算总执行时间
        total_duration = sum(r["duration"] for r in reports)
        
        # 添加到摘要
        summary[model] = {
            "avg_score": round(avg_score, 2),
            "dimension_scores": {dim: round(score, 2) for dim, score in dimension_scores.items()},
            "total_tokens": total_tokens,
            "total_duration": total_duration,
            "report_count": len(reports)
        }
    
    # 保存摘要
    summary_file = os.path.join(output_dir, "benchmark_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"Benchmark摘要已保存到: {summary_file}")

def main():
    # 当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 加载报告
    print("从MD文件中加载报告...")
    all_reports, report_to_model_map = load_reports_from_md(current_dir)
    print(f"找到 {len(all_reports)} 个报告")
    
    if not all_reports:
        print("未找到任何报告，无法生成比较结果")
        return
    
    # 生成pipeline比较报告
    print("生成pipeline比较报告...")
    generate_pipeline_comparison_report(all_reports, report_to_model_map, current_dir)
    
    # 生成benchmark摘要
    print("生成benchmark摘要...")
    generate_benchmark_summary(all_reports, report_to_model_map, current_dir)
    
    print("所有报告已生成完成！")

if __name__ == "__main__":
    main()
