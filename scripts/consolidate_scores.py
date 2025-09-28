import os
import re
import glob
import json
import pandas as pd
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

# 忽略 pandas 的 FutureWarning，因为它不影响当前计算结果
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw_run_data')
SUMMARY_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, 'workspace')

# Define output file
OUTPUT_CSV = os.path.join(SUMMARY_DATA_DIR, "raw_scores_collection.csv")

# Define input directories for all runs
QWEN_MAX_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250630_214742", "run_20250701_155804", "run_20250701_181915",
    "run_20250630_201054", "run_20250630_185156", "run_20250630_163324",
    "run_20250630_003147"
]]
PIPELINE_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250711_204700", "run_20250712_203413", "run_20250713_004043",
    "run_20250713_024028", "run_20250713_034721"
]]
METAGPT_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250713_223534", "run_20250713_225157", "run_20250713_225853",
    "run_20250713_230819", "run_20250713_231639", "run_20250714_104334",
    "run_20250714_110732"
]]
QWEN_MAX_LATEST_PIPELINE_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250714_202550", "run_20250714_205741", "run_20250714_211504",
    "run_20250714_213332", "run_20250714_215025"
]]
DEEPSEEK_V3_PIPELINE_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250716_101039", "run_20250716_103208", "run_20250716_105214",
    "run_20250716_115725", "run_20250716_111320"
]]

# --- Utility Functions ---

def _get_simplified_server_mapping() -> Dict[str, str]:
    """Returns a mapping from long server names to simplified, capitalized names."""
    mapping = {
        "academic-search-mcp-server-master": "Academic Search", "arxiv-mcp-server-main": "Arxiv",
        "duckduckgo-mcp-server-main": "Duckduckgo", "flights-mcp-main": "Flights",
        "huggingface-mcp-server-main": "Huggingface", "image-file-converter-mcp-server-main": "Image Converter",
        "markitdown-main": "Markdown", "mcp-doc-main": "Word Automation (Doc)",
        "office-word-mcp-server-main": "Word Processor (Office)", "mcp-everything-search-main": "Everything Search",
        "mcp-official-git": "Git", "mcp-pdf-tools": "Pdf Tools",
        "mcp-server-data-exploration-main": "Data Exploration", "mcp-server-main": "Financial Data",
        "mcp-tavily-main": "Tavily", "mcp-text-editor-main": "Text Editor",
        "mcp_search_images-main": "Image Search", "mongo-mcp-main": "Mongodb",
        "my-mcp-ssh-master": "Ssh", "mysql_mcp_server-main": "Mysql",
        "opencv-mcp-server-main": "Opencv", "outlook-mcp-server-main": "Outlook",
        "screenshot-server-main": "Screenshot", "unsplash-mcp-server-main": "Unsplash",
        "zotero-mcp-main": "Zotero",
    }
    return mapping

def _simplify_name(name: str, mapping: Dict[str, str]) -> str:
    """Uses the provided mapping to simplify a server name."""
    return mapping.get(name.lower().strip(), name.strip())

def _get_metagpt_reverse_mapping() -> Dict[Tuple[str, str], str]:
    """Loads pipeline_mapping.json and creates a reverse lookup map from (model, project) to public_server_name."""
    mapping_file = os.path.join(WORKSPACE_DIR, 'pipeline_mapping.json')
    reverse_mapping = {}
    
    if not os.path.exists(mapping_file):
        print(f"  - 警告: pipeline_mapping.json not found at {mapping_file}")
        return {}

    with open(mapping_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        public_name = item.get('public_server_name')
        if not public_name: continue
        
        for model, server_info in item.get('generated_servers', {}).items():
            if server_info and 'project_name' in server_info:
                project_name = server_info['project_name']
                # Key: (model_name, project_raw_name) -> public_server_name
                reverse_mapping[(model, project_name)] = public_name
                
    return reverse_mapping

# --- Data Parsing Functions ---

def parse_qwen_max_runs(run_dirs: List[str], mapping: Dict[str, str]) -> List[Dict]:
    """
    Parses the 7 old Qwen-Max runs by reading the summary table from *comparison_report.md files.
    This logic is adapted from old_compare-all.py.
    """
    all_data = []
    # Regex to capture the full data row from the markdown table
    table_pattern = re.compile(r'\|\s*([a-zA-Z-].*?)\s*\|\s*([\d\.]+)\s*\|(.*?)\|\s*([\d\.]+)\s*\|.*')

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        report_file_path = glob.glob(os.path.join(run_dir, "*comparison_report.md"))
        if not report_file_path:
            print(f"  - 警告: 在 {run_name} 中未找到 comparison_report.md。")
            continue
        
        print(f"正在处理 Qwen-MAX 运行: {run_name}")
        public_scores = {'Test Subject': 'Public Baseline', 'Run Source': run_name}
        qwen_max_scores = {'Test Subject': 'qwen-max', 'Run Source': run_name}

        with open(report_file_path[0], 'r', encoding='utf-8') as f:
            content = f.read()

        matches = table_pattern.findall(content)
        for row in matches:
            public_server, public_score, _, refined_score = row
            simplified_name = _simplify_name(public_server, mapping)
            public_scores[simplified_name] = float(public_score)
            qwen_max_scores[simplified_name] = float(refined_score)
        
        if len(public_scores) > 2: # Check if any scores were actually added
            all_data.append(public_scores)
            all_data.append(qwen_max_scores)
        else:
            print(f"  - 警告: 在 {os.path.basename(report_file_path[0])} 中未解析到任何有效分数。")

    return all_data

def parse_pipeline_runs(run_dirs: List[str], mapping: Dict[str, str]) -> List[Dict]:
    """
    Parses the 5 new pipeline runs by reading pipeline_detailed_scores.csv from each run directory.
    This logic is adapted from final_analysis.py.
    """
    all_data = []
    dim_cols = ["功能性", "健壮性", "安全性", "性能", "透明性"]

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        csv_path = os.path.join(run_dir, "pipeline_detailed_scores.csv")
        
        if not os.path.exists(csv_path):
            print(f"  - 警告: 在 {run_name} 中未找到 pipeline_detailed_scores.csv。")
            continue
            
        print(f"正在处理 Pipeline 运行: {run_name}")
        df_run = pd.read_csv(csv_path)
        
        # Calculate total score from dimensions
        df_run['total_score'] = df_run[dim_cols].sum(axis=1)
        
        # Pivot table to get scores for each model
        pivot = df_run.pivot_table(index='model', columns='public_server_name', values='total_score')
        
        for model_name, scores in pivot.iterrows():
            record = {'Test Subject': model_name, 'Run Source': run_name}
            for server_name, score in scores.items():
                simplified_name = _simplify_name(server_name, mapping)
                record[simplified_name] = score
            all_data.append(record)
            
    return all_data

def parse_metagpt_runs(run_dirs: List[str], reverse_mapping: Dict, simplified_name_mapping: Dict) -> List[Dict]:
    """
    Parses the new MetaGPT runs by reading detailed_report_*.md files and extracting the total score.
    """
    all_data = []
    # Regex to find the total score in the <SCORES> block
    score_pattern = re.compile(r"总分:\s*(\d+)/100")

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        print(f"正在处理 MetaGPT 运行: {run_name}")

        base_path = os.path.join(run_dir, "metaGPT-servers")
        if not os.path.exists(base_path):
            print(f"  - 警告: 在 {run_name} 中未找到 metaGPT-servers 目录。")
            continue
        
        # This dict will hold scores for one run, keyed by the model name (e.g., 'metaGPT-qwen-plus')
        run_scores_by_model = {}

        # Find all model directories within the run, e.g., .../metaGPT-servers/metaGPT-qwen-plus
        model_dirs = [d for d in glob.glob(os.path.join(base_path, "*")) if os.path.isdir(d)]
        
        for model_dir in model_dirs:
            model_name = os.path.basename(model_dir)
            if model_name not in run_scores_by_model:
                run_scores_by_model[model_name] = {'Test Subject': model_name, 'Run Source': run_name}

            # Find all detailed report files within the model's directory
            report_files = glob.glob(os.path.join(model_dir, "detailed_report_*.md"))

            for report_path in report_files:
                filename = os.path.basename(report_path)
                
                # Extract raw project name from filename
                # e.g., "detailed_report_metaGPT-qwen-plus-financial_data_mcp_server.md"
                # -> we need "financial_data_mcp_server"
                prefix_to_remove = f"detailed_report_{model_name}-"
                if filename.startswith(prefix_to_remove):
                     project_name_raw = filename[len(prefix_to_remove):].replace('.md', '')
                else:
                    print(f"  - 警告: 无法从文件名 {filename} 解析项目名称")
                    continue
                
                # Find public server name from reverse mapping
                public_server_name = reverse_mapping.get((model_name, project_name_raw))
                if not public_server_name:
                     print(f"  - 警告: 在映射中未找到项目 ({model_name}, {project_name_raw})")
                     continue
                
                simplified_name = _simplify_name(public_server_name, simplified_name_mapping)

                # Extract score from file content
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                match = score_pattern.search(content)
                if match:
                    score = float(match.group(1))
                    run_scores_by_model[model_name][simplified_name] = score
                else:
                    print(f"  - 警告: 在 {filename} 中未找到总分。")
        
        # Add the collected scores for this run to the final list
        for model_data in run_scores_by_model.values():
            if len(model_data) > 2: # Ensure some scores were actually added
                all_data.append(model_data)

    return all_data

def parse_qwen_max_latest_pipeline_runs(run_dirs: List[str], reverse_mapping: Dict, simplified_name_mapping: Dict) -> List[Dict]:
    """
    Parses the new qwen-max-latest pipeline runs by reading detailed_report_*.md files.
    """
    all_data = []
    score_pattern = re.compile(r"总分:\s*(\d+)/100")
    model_name = "qwen-max-latest"  # The model is fixed for these runs

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        print(f"正在处理 qwen-max-latest Pipeline 运行: {run_name}")

        base_path = os.path.join(run_dir, "pipeline_server_tests", model_name)
        if not os.path.exists(base_path):
            print(f"  - 警告: 在 {run_name} 中未找到 {base_path} 目录。")
            continue
        
        # This dict will hold scores for this single model in this single run
        run_scores = {'Test Subject': model_name, 'Run Source': run_name}

        report_files = glob.glob(os.path.join(base_path, "detailed_report_*.md"))

        for report_path in report_files:
            filename = os.path.basename(report_path)
            
            # Extract raw project name from filename
            # e.g., "detailed_report_qwen-max-latest-mcp_data_explorer_analyzer.md"
            prefix_to_remove = f"detailed_report_{model_name}-"
            if filename.startswith(prefix_to_remove):
                 project_name_raw = filename[len(prefix_to_remove):].replace('.md', '')
            else:
                print(f"  - 警告: 无法从文件名 {filename} 解析项目名称")
                continue
            
            # Find public server name from reverse mapping
            # The key for reverse_mapping is (model_name, project_raw_name)
            # The project_name_raw for qwen-max-latest has been changed in main.py, so we need to match it
            
            # First, find the corresponding public server entry
            matched_public_server = None
            for key, pub_name in reverse_mapping.items():
                # key is a tuple: (model, project_name)
                if key[0] == model_name and key[1] in project_name_raw:
                    matched_public_server = pub_name
                    break
            
            if not matched_public_server:
                # Fallback for cases where the project name might be slightly different
                # This part needs careful adjustment based on actual naming conventions
                # Let's try a simpler direct lookup first.
                public_server_name = reverse_mapping.get((model_name, project_name_raw))
                if not public_server_name:
                    print(f"  - 警告: 在映射中未找到项目 ({model_name}, {project_name_raw})")
                    continue
            else:
                public_server_name = matched_public_server

            simplified_name = _simplify_name(public_server_name, simplified_name_mapping)

            # Extract score from file content
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = score_pattern.search(content)
            if match:
                score = float(match.group(1))
                run_scores[simplified_name] = score
            else:
                print(f"  - 警告: 在 {filename} 中未找到总分。")
        
        # Add the collected scores for this run to the final list
        if len(run_scores) > 2: # Ensure some scores were actually added
            all_data.append(run_scores)

    return all_data

def parse_deepseek_v3_pipeline_runs(run_dirs: List[str], reverse_mapping: Dict, simplified_name_mapping: Dict) -> List[Dict]:
    """
    Parses the new deepseek-v3 pipeline runs by reading detailed_report_*.md files.
    """
    all_data = []
    score_pattern = re.compile(r"总分:\s*(\d+)/100")
    model_name = "deepseek-v3"  # The model is fixed for these runs

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        print(f"正在处理 deepseek-v3 Pipeline 运行: {run_name}")

        base_path = os.path.join(run_dir, "pipeline_server_tests", model_name)
        if not os.path.exists(base_path):
            print(f"  - 警告: 在 {run_name} 中未找到 {base_path} 目录。")
            continue
        
        # This dict will hold scores for this single model in this single run
        run_scores = {'Test Subject': model_name, 'Run Source': run_name}

        report_files = glob.glob(os.path.join(base_path, "detailed_report_*.md"))

        for report_path in report_files:
            filename = os.path.basename(report_path)
            
            # Extract raw project name from filename
            # e.g., "detailed_report_deepseek-v3-mcp_data_explorer_analyzer.md"
            prefix_to_remove = f"detailed_report_{model_name}-"
            if filename.startswith(prefix_to_remove):
                 project_name_raw = filename[len(prefix_to_remove):].replace('.md', '')
            else:
                print(f"  - 警告: 无法从文件名 {filename} 解析项目名称")
                continue
            
            # Find public server name from reverse mapping
            # The key for reverse_mapping is (model_name, project_raw_name)
            
            # First, find the corresponding public server entry
            matched_public_server = None
            for key, pub_name in reverse_mapping.items():
                # key is a tuple: (model, project_name)
                if key[0] == model_name and key[1] in project_name_raw:
                    matched_public_server = pub_name
                    break
            
            if not matched_public_server:
                # Fallback for cases where the project name might be slightly different
                # This part needs careful adjustment based on actual naming conventions
                # Let's try a simpler direct lookup first.
                public_server_name = reverse_mapping.get((model_name, project_name_raw))
                if not public_server_name:
                    print(f"  - 警告: 在映射中未找到项目 ({model_name}, {project_name_raw})")
                    continue
            else:
                public_server_name = matched_public_server

            simplified_name = _simplify_name(public_server_name, simplified_name_mapping)

            # Extract score from file content
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = score_pattern.search(content)
            if match:
                score = float(match.group(1))
                run_scores[simplified_name] = score
            else:
                print(f"  - 警告: 在 {filename} 中未找到总分。")
        
        # Add the collected scores for this run to the final list
        if len(run_scores) > 2: # Ensure some scores were actually added
            all_data.append(run_scores)

    return all_data


# --- Main Execution ---

def main():
    """Main function to orchestrate parsing, consolidation, and saving."""
    print("开始整合所有原始分数数据...")
    server_mapping = _get_simplified_server_mapping()
    score_columns = sorted(list(server_mapping.values()))
    
    print("\n--- (1/3) 解析 Qwen-MAX (旧版) 运行... ---")
    qwen_max_data = parse_qwen_max_runs(QWEN_MAX_RUNS, server_mapping)
    
    print("\n--- (2/3) 解析 Pipeline (新版) 运行... ---")
    pipeline_data = parse_pipeline_runs(PIPELINE_RUNS, server_mapping)
    
    print("\n--- (3/3) 解析 MetaGPT (新版) 运行... ---")
    metagpt_reverse_mapping = _get_metagpt_reverse_mapping()
    metagpt_data = parse_metagpt_runs(METAGPT_RUNS, metagpt_reverse_mapping, server_mapping)
    
    print("\n--- (4/4) 解析 qwen-max-latest Pipeline 运行... ---")
    qwen_latest_data = parse_qwen_max_latest_pipeline_runs(QWEN_MAX_LATEST_PIPELINE_RUNS, metagpt_reverse_mapping, server_mapping)

    print("\n--- (5/5) 解析 deepseek-v3 Pipeline 运行... ---")
    deepseek_v3_data = parse_deepseek_v3_pipeline_runs(DEEPSEEK_V3_PIPELINE_RUNS, metagpt_reverse_mapping, server_mapping)


    all_run_data = qwen_max_data + pipeline_data + metagpt_data + qwen_latest_data + deepseek_v3_data
    
    if not all_run_data:
        print("\n错误: 未能从任何来源收集到有效数据。请检查路径和文件格式。")
        return
        
    df = pd.DataFrame(all_run_data)
    
    # --- 新增统计分析 ---
    print("\n--- (5/5) 计算统计数据... ---")

    # 1. 标准化列并填充缺失值
    base_columns = ['Test Subject', 'Run Source']
    stats_columns = ['Average score', 'Standard deviation', 'Testable Tasks', 'Testability Rate']
    for col in score_columns:
        if col not in df.columns:
            df[col] = 0.0
            
    df = df[base_columns + score_columns].fillna(0.0)

    # 2. 计算每行的统计数据 (排除零分)
    scores_df = df[score_columns]
    scores_nan = scores_df.astype(float).replace(0, pd.NA)
    
    df['Average score'] = scores_nan.mean(axis=1)
    df['Standard deviation'] = scores_nan.std(axis=1)
    df['Testable Tasks'] = scores_nan.count(axis=1)
    df['Testability Rate'] = scores_nan.count(axis=1) / len(score_columns)

    # 3. 计算每个模型的聚合统计数据并与基线对比
    model_agg_rows = []

    # 首先计算并储存基线的平均分 (纯数字)
    baseline_df = df[df['Test Subject'] == 'Public Baseline']
    baseline_scores_nan = baseline_df[score_columns].astype(float).replace(0, pd.NA)
    baseline_avg_scores = baseline_scores_nan.mean().fillna(0)

    # 创建一个纯数字的平均分DataFrame，用于计算行末的统计数据
    all_models_avg_numeric = {}
    for model_name in df['Test Subject'].unique():
        model_df = df[df['Test Subject'] == model_name]
        model_scores_nan = model_df[score_columns].astype(float).replace(0, pd.NA)
        all_models_avg_numeric[model_name] = model_scores_nan.mean().fillna(0)

    # 现在创建用于显示的格式化行
    for model_name in df['Test Subject'].unique():
        model_avg_scores = all_models_avg_numeric[model_name]
        
        agg_row = {'Test Subject': f"{model_name}-ave"}

        # 格式化每个任务的分数
        for col in score_columns:
            model_avg = model_avg_scores.get(col, 0)
            
            # 统一格式：所有模型行都显示 "均值 (±与基线差异)"
            baseline_avg = baseline_avg_scores.get(col, 0)
            diff = model_avg - baseline_avg
            agg_row[col] = f"{model_avg:.2f} ({diff:+.2f})"

        # 计算行末的总体统计数据 (基于纯数字的平均分)
        agg_row_scores = model_avg_scores[model_avg_scores > 0]
        agg_row['Average score'] = agg_row_scores.mean() if not agg_row_scores.empty else 0
        agg_row['Standard deviation'] = agg_row_scores.std() if not agg_row_scores.empty else 0
        agg_row['Testable Tasks'] = agg_row_scores.count()
        agg_row['Testability Rate'] = agg_row_scores.count() / len(score_columns)
        
        model_agg_rows.append(agg_row)
        
    # 4. 合并和排序
    agg_df = pd.DataFrame(model_agg_rows)

    # 对原始数据和聚合数据中的数字列进行四舍五入
    df[score_columns + stats_columns] = df[score_columns + stats_columns].round(2)
    agg_df[stats_columns] = agg_df[stats_columns].round(2)

    combined_df = pd.concat([df, agg_df], ignore_index=True)
    
    # 创建辅助列以正确排序，将-ave行放在每个模型的末尾
    combined_df['model_group'] = combined_df['Test Subject'].str.replace('-ave', '')
    combined_df['is_ave'] = combined_df['Test Subject'].str.contains('-ave')
    
    combined_df.sort_values(
        by=['model_group', 'is_ave', 'Run Source'], 
        inplace=True, 
        ignore_index=True,
        na_position='last'
    )

    # 5. 最终格式化并保存
    final_column_order = ['Test Subject'] + score_columns + stats_columns
    
    # 删除辅助列和 'Run Source'
    df_final = combined_df.drop(columns=['Run Source', 'model_group', 'is_ave'], errors='ignore')
    
    df_final = df_final[final_column_order]
    df_final.fillna(0, inplace=True) 

    # 保存到CSV
    df_final.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print(f"\n数据整合完成！共找到 {len(df_final)} 条记录。")
    print(f"包含统计分析的原始分数数据已保存到: {OUTPUT_CSV}")

if __name__ == "__main__":
    main() 