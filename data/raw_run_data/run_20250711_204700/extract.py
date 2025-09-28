#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 项目名称映射
PROJECT_NAME_MAPPING = {
    "academic_paper": "Academic Search",
    "arxiv": "Arxiv",
    "data_explorer": "Data Exploration",
    "duckduckgo": "Duckduckgo",
    "everything": "Everything Search",
    "financial": "Financial Data",
    "flight": "Flights",
    "git": "Git",
    "huggingface": "Huggingface",
    "image_format_converter": "Image Converter",
    "image_icon": "Image Search",
    "markdown": "Markdown",
    "mongodb": "Mongodb",
    "mysql": "Mysql",
    "opencv": "Opencv",
    "outlook": "Outlook",
    "pdf": "Pdf Tools",
    "screenshot": "Screenshot",
    "ssh": "Ssh",
    "tavily": "Tavily",
    "text_file": "Text Editor",
    "unsplash": "Unsplash",
    "word_document_automation": "Word Automation (Doc)",
    "word_document_processor": "Word Processor (Office)",
    "zotero": "Zotero"
}

def extract_model_name(project_name: str) -> str:
    """从项目名称中提取模型名称"""
    if project_name.startswith("2.5-pro-"):
        return "gemini-2.5-pro"
    elif project_name.startswith("4o-"):
        return "gpt-4o"
    elif project_name.startswith("plus-"):
        return "qwen-plus"
    return "unknown"

def extract_project_type(project_name: str) -> str:
    """从项目名称中提取项目类型"""
    # 移除模型前缀
    if project_name.startswith("2.5-pro-"):
        project_name = project_name[8:]
    elif project_name.startswith("4o-"):
        project_name = project_name[3:]
    elif project_name.startswith("plus-"):
        project_name = project_name[5:]
    
    # 提取项目类型
    for key in PROJECT_NAME_MAPPING.keys():
        if key in project_name.lower():
            return PROJECT_NAME_MAPPING[key]
    
    # 如果没有匹配，尝试更具体的匹配
    if "academic" in project_name.lower():
        return "Academic Search"
    elif "arxiv" in project_name.lower():
        return "Arxiv"
    elif "data" in project_name.lower() and ("explor" in project_name.lower() or "analy" in project_name.lower()):
        return "Data Exploration"
    elif "duck" in project_name.lower():
        return "Duckduckgo"
    elif "everything" in project_name.lower() or "file_search" in project_name.lower():
        return "Everything Search"
    elif "financial" in project_name.lower():
        return "Financial Data"
    elif "flight" in project_name.lower() or "duffeld" in project_name.lower():
        return "Flights"
    elif "git" in project_name.lower():
        return "Git"
    elif "huggingface" in project_name.lower():
        return "Huggingface"
    elif "image_format" in project_name.lower() or "image_converter" in project_name.lower():
        return "Image Converter"
    elif "image" in project_name.lower() and ("search" in project_name.lower() or "icon" in project_name.lower()):
        return "Image Search"
    elif "markdown" in project_name.lower():
        return "Markdown"
    elif "mongodb" in project_name.lower():
        return "Mongodb"
    elif "mysql" in project_name.lower():
        return "Mysql"
    elif "opencv" in project_name.lower() or "vision" in project_name.lower():
        return "Opencv"
    elif "outlook" in project_name.lower():
        return "Outlook"
    elif "pdf" in project_name.lower():
        return "Pdf Tools"
    elif "screenshot" in project_name.lower():
        return "Screenshot"
    elif "ssh" in project_name.lower():
        return "Ssh"
    elif "tavily" in project_name.lower():
        return "Tavily"
    elif "text_file" in project_name.lower():
        return "Text Editor"
    elif "unsplash" in project_name.lower():
        return "Unsplash"
    elif "word" in project_name.lower() and "automation" in project_name.lower():
        return "Word Automation (Doc)"
    elif "word" in project_name.lower() and "processor" in project_name.lower():
        return "Word Processor (Office)"
    elif "zotero" in project_name.lower():
        return "Zotero"
    
    return "Unknown"

def extract_scores_from_md(md_file: str) -> Dict:
    """从MD文件中提取得分信息"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试提取总分
        score_match = re.search(r'总分：(\d+)/100', content)
        if score_match:
            total_score = int(score_match.group(1))
            return {"total_score": total_score}
        
        # 尝试提取英文总分
        score_match_en = re.search(r'Total Score: (\d+)/100', content)
        if score_match_en:
            total_score = int(score_match_en.group(1))
            return {"total_score": total_score}
        
        # 如果没有找到总分，尝试从SCORES标签中提取
        scores_pattern = r'<SCORES>(.*?)</SCORES>'
        scores_match = re.search(scores_pattern, content, re.DOTALL)
        
        if scores_match:
            scores_text = scores_match.group(1).strip()
            total_score_match = re.search(r'总分：(\d+)/100', scores_text)
            if total_score_match:
                total_score = int(total_score_match.group(1))
                return {"total_score": total_score}
            
            total_score_match_en = re.search(r'Total Score: (\d+)/100', scores_text)
            if total_score_match_en:
                total_score = int(total_score_match_en.group(1))
                return {"total_score": total_score}
    except Exception as e:
        print(f"从文件 {md_file} 提取得分时出错: {str(e)}")
    
    # 如果都没有找到，返回0分
    return {"total_score": 0}

def parse_pipeline_report(report_file: str) -> Dict:
    """解析pipeline比较报告"""
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取表格数据
        table_pattern = r'\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|'
        table_matches = re.findall(table_pattern, content)
        
        # 跳过表头和分隔行
        data_rows = table_matches[2:]  # 跳过表头和分隔行
        
        # 创建项目分组
        project_scores = {}
        
        for row in data_rows:
            project_name = row[0].strip()
            if project_name == "Average Score":
                continue
            
            # 提取模型名称和项目类型
            model_name = extract_model_name(project_name)
            project_type = extract_project_type(project_name)
            
            # 提取得分
            if project_name.startswith("2.5-pro-"):
                score = int(row[1].strip()) if row[1].strip() and row[1].strip() != '0' else 0
            elif project_name.startswith("4o-"):
                score = int(row[2].strip()) if row[2].strip() and row[2].strip() != '0' else 0
            elif project_name.startswith("plus-"):
                score = int(row[3].strip()) if row[3].strip() and row[3].strip() != '0' else 0
            else:
                continue
            
            # 添加到项目分组
            if project_type not in project_scores:
                project_scores[project_type] = {
                    "gemini-2.5-pro": 0,
                    "gpt-4o": 0,
                    "qwen-plus": 0
                }
            
            project_scores[project_type][model_name] = score
        
        return project_scores
    except Exception as e:
        print(f"解析pipeline报告时出错: {str(e)}")
        return {}

def extract_data_from_detailed_reports(base_dir: str) -> Dict:
    """从详细报告中提取数据"""
    all_data = {}
    
    # 查找所有详细报告MD文件
    detailed_report_files = glob.glob(os.path.join(base_dir, "pipeline_server_tests", "detailed_report_*.md"))
    
    for report_file in detailed_report_files:
        try:
            # 提取报告名称
            report_name = os.path.basename(report_file).replace("detailed_report_", "").replace(".md", "")
            
            # 提取得分
            scores = extract_scores_from_md(report_file)
            
            # 提取模型名称
            model_name = extract_model_name(report_name)
            
            # 提取项目类型
            project_type = extract_project_type(report_name)
            
            # 添加到结果字典
            if project_type not in all_data:
                all_data[project_type] = {
                    "gemini-2.5-pro": 0,
                    "gpt-4o": 0,
                    "qwen-plus": 0
                }
            
            all_data[project_type][model_name] = scores["total_score"]
            
            print(f"已加载报告: {report_name} | 项目: {project_type} | 模型: {model_name} | 得分: {scores['total_score']}")
        except Exception as e:
            print(f"处理报告 {report_file} 时出错: {str(e)}")
    
    return all_data

def generate_pipeline_comparison_report(all_data: Dict, output_dir: str):
    """生成pipeline比较报告"""
    print("\n====== 生成Pipeline比较报告 ======")
    
    # 创建DataFrame
    df_data = []
    for project_name, scores in all_data.items():
        df_data.append({
            "public_server_name": project_name,
            "gemini-2.5-pro": scores["gemini-2.5-pro"],
            "gpt-4o": scores["gpt-4o"],
            "qwen-plus": scores["qwen-plus"]
        })
    
    df = pd.DataFrame(df_data)
    
    # 计算平均分（忽略0分，即0分不计入分母）
    avg_gemini = df["gemini-2.5-pro"].replace(0, np.nan).mean()
    avg_gpt = df["gpt-4o"].replace(0, np.nan).mean()
    avg_qwen = df["qwen-plus"].replace(0, np.nan).mean()

    # 处理所有分数都为0的情况，避免NaN
    avg_gemini = 0 if pd.isna(avg_gemini) else avg_gemini
    avg_gpt = 0 if pd.isna(avg_gpt) else avg_gpt
    avg_qwen = 0 if pd.isna(avg_qwen) else avg_qwen
    
    # 添加平均分行
    df.loc[len(df)] = {
        "public_server_name": "**Average Score**",
        "gemini-2.5-pro": round(avg_gemini, 2),
        "gpt-4o": round(avg_gpt, 2),
        "qwen-plus": round(avg_qwen, 2)
    }
    
    # 生成Markdown报告
    report = "# Pipeline Model Performance Comparison Report\n\n"
    report += "This report compares the performance of different AI models on the same server generation tasks.\n\n"
    
    # 添加总分比较表格
    report += "## 1. Overall Score Comparison (Higher is Better)\n\n"
    report += df.to_markdown(index=False) + "\n\n"
    
    # 保存报告
    report_file = os.path.join(output_dir, "pipeline_comparison_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Pipeline比较报告已保存到: {report_file}")
    
    # 生成可视化图表
    generate_pipeline_comparison_chart(df, output_dir)

def generate_pipeline_comparison_chart(df: pd.DataFrame, output_dir: str):
    """生成pipeline比较图表"""
    # 移除平均分行
    chart_df = df[df["public_server_name"] != "**Average Score**"].copy()
    
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

def generate_mapping_json(all_data: Dict, output_dir: str):
    """生成映射JSON文件"""
    print("\n====== 生成映射JSON文件 ======")
    
    # 创建映射数据
    mapping_data = []
    for project_name, scores in all_data.items():
        mapping_item = {
            "public_server_name": project_name.lower(),
            "generated_servers": {}
        }
        
        # 添加模型信息
        for model_name in ["gemini-2.5-pro", "gpt-4o", "qwen-plus"]:
            if scores[model_name] > 0:
                mapping_item["generated_servers"][model_name] = {
                    "project_name": f"{model_name}-{project_name.lower().replace(' ', '_')}",
                    "server_path": ""  # 没有实际路径信息
                }
        
        mapping_data.append(mapping_item)
    
    # 保存映射文件
    mapping_file = os.path.join(output_dir, "pipeline_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent=2)
    
    print(f"映射JSON文件已保存到: {mapping_file}")

def main():
    # 当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试从pipeline_comparison_report.md中提取数据
    pipeline_report_path = os.path.join(current_dir, "pipeline_server_tests", "pipeline_comparison_report.md")
    if os.path.exists(pipeline_report_path):
        print("从pipeline_comparison_report.md中提取数据...")
        all_data = parse_pipeline_report(pipeline_report_path)
    else:
        # 从详细报告中提取数据
        print("从详细报告中提取数据...")
        all_data = extract_data_from_detailed_reports(current_dir)
    
    if not all_data:
        print("未找到任何数据，无法生成比较结果")
        return
    
    # 生成pipeline比较报告
    print("生成pipeline比较报告...")
    generate_pipeline_comparison_report(all_data, current_dir)
    
    # 生成映射JSON文件
    print("生成映射JSON文件...")
    generate_mapping_json(all_data, current_dir)
    
    print("所有报告已生成完成！")

if __name__ == "__main__":
    main()
