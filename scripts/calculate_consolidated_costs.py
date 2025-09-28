import os
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List
import json

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
SUMMARY_DATA_DIR = PROJECT_ROOT / "data" / "summary_data"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"

PIPELINE_OUTPUT_DIR = WORKSPACE_DIR / "pipeline-output-servers"
PIPELINE_MAPPING_PATH = WORKSPACE_DIR / "pipeline_mapping.json"
OLD_VERSION_REPORT = SUMMARY_DATA_DIR / "old_version_token_consumption_report.md"
OUTPUT_CSV = SUMMARY_DATA_DIR / "average_costs.csv"
RMB_TO_USD_RATE = 7.2

# --- Utility Functions ---

def _get_simplified_server_mapping() -> Dict[str, str]:
    """
    Dynamically generates a server name mapping from 'pipeline_mapping.json'.
    This mapping converts various project names (public, model-specific) 
    into a consistent, simplified name.
    """
    print("--- (0/3) Generating server name mapping from pipeline_mapping.json ---")
    mapping = {}
    try:
        with open(PIPELINE_MAPPING_PATH, 'r', encoding='utf-8') as f:
            pipeline_data = json.load(f)
        
        for project_group in pipeline_data:
            simplified_name = project_group.get('simplified_name')
            if not simplified_name:
                continue

            # Map public server name (normalized to lowercase)
            if 'public_server_name' in project_group:
                mapping[project_group['public_server_name'].lower()] = simplified_name

            # Map all generated server project names (normalized to lowercase)
            if 'generated_servers' in project_group:
                for model, server_info in project_group['generated_servers'].items():
                    if server_info and 'project_name' in server_info:
                        mapping[server_info['project_name'].lower()] = simplified_name
        
        print(f"  - Successfully created mapping for {len(mapping)} unique project names.")
        return mapping
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  - Error reading or parsing pipeline_mapping.json: {e}")
        print("  - Falling back to an empty mapping.")
        return {}


def _simplify_name(name: str, mapping: Dict[str, str]) -> str:
    """
    Uses the provided mapping to simplify a server name, ignoring case 
    and handling '_refined' suffix inconsistencies.
    """
    # Normalize the input name to match the mapping keys' format
    processed_name = name.lower().strip()
    
    # 1. Direct match on processed name
    if processed_name in mapping:
        return mapping[processed_name]
    
    # 2. Match without '_refined' suffix
    if processed_name.endswith('_refined'):
        base_name = processed_name.removesuffix('_refined')
        if base_name in mapping:
            return mapping[base_name]

    # 3. Match WITH '_refined' suffix (for names that are missing it in the source)
    name_with_refined = f"{processed_name}_refined"
    if name_with_refined in mapping:
        return mapping[name_with_refined]
        
    # Fallback to the original name if no mapping is found
    return name.strip()

# --- Data Parsing Functions ---

def parse_qwen_max_costs(report_path: Path, mapping: Dict[str, str]) -> List[Dict]:
    """Parses the old Qwen-Max cost report and converts cost to USD."""
    print("\n--- (1/3) Parsing Qwen-MAX Cost Report ---")
    if not report_path.exists():
        print(f"  - 警告: Qwen-MAX报告未找到于: {report_path}")
        return []
    with open(report_path, 'r', encoding='utf-8') as f: content = f.read()
    data, project_sections = [], re.split(r'## Project: `', content)[1:]
    for section in project_sections:
        project_name = re.match(r'(.+?)`', section).group(1)
        simplified_name = _simplify_name(project_name, mapping)
        total_line = re.search(r'\|\s*\*\*Project Total\*\*.*?\|.*?([\d,]+)\*\*.*?\*\*¥\s*([\d,.]+)\*\*', section, re.DOTALL)
        if total_line:
            tokens, cost_rmb = int(total_line.group(1).replace(',', '')), float(total_line.group(2).replace(',', ''))
            cost_usd = cost_rmb / RMB_TO_USD_RATE
            data.append({'Model': 'qwen-max', 'Server Name': simplified_name, 'Total Tokens': tokens, 'Total Cost (USD)': cost_usd})
            print(f"  - 找到 Qwen-MAX for '{simplified_name}': {tokens} tokens, ¥{cost_rmb:.4f} -> ${cost_usd:.4f}")
    return data

def parse_pipeline_costs(base_dir: Path, mapping: Dict[str, str]) -> List[Dict]:
    """Parses pipeline output directories and converts cost to USD."""
    print(f"\n--- (2/3) Parsing Pipeline Cost Reports from {base_dir} ---")
    data = []
    models = ['gpt-4o', 'qwen-plus', 'gemini-2.5-pro']
    for model in models:
        model_path = base_dir / model
        if not model_path.is_dir(): continue
        print(f"  - Processing model: {model.upper()}")
        for project_dir in model_path.iterdir():
            if not project_dir.is_dir(): continue
            
            report_path = None
            if (project_dir / "statistics_report.md").exists():
                report_path = project_dir / "statistics_report.md"
            elif (project_dir / "refined" / "statistics_report.md").exists():
                report_path = project_dir / "refined" / "statistics_report.md"
            
            if report_path:
                simplified_name = _simplify_name(project_dir.name, mapping)
                with open(report_path, 'r', encoding='utf-8') as f: content = f.read()
                
                matches = re.findall(r"模型: `(.+?)`.*?总成本\s*\(RMB\)\*\*\s*\|\s*\*\*¥([\d,.]+)\*\*.*?总 Token\s*\|\s*([\d,]+)", content, re.DOTALL)
                
                if matches:
                    total_tokens = 0
                    total_cost_usd = 0.0
                    
                    # 细化成本计算逻辑：逐个模型处理
                    for model_name_from_report, cost_str, tokens_str in matches:
                        tokens = int(tokens_str.replace(',', ''))
                        cost_val = float(cost_str.replace(',', ''))
                        
                        # 关键修正：Gemini 的成本单位是美元，其他模型是人民币
                        if 'gemini-2.5-pro' in model_name_from_report:
                            cost_in_usd = cost_val  # 直接视为美元
                        else:
                            cost_in_usd = cost_val / RMB_TO_USD_RATE  # 从人民币转换为美元
                            
                        total_tokens += tokens
                        total_cost_usd += cost_in_usd
                    
                    data.append({'Model': model, 'Server Name': simplified_name, 'Total Tokens': total_tokens, 'Total Cost (USD)': total_cost_usd})
                    print(f"    - 找到 {model.upper()} for '{simplified_name}': {total_tokens} tokens, ${total_cost_usd:.4f}")
    return data

# --- Main Execution ---
def main():
    """
    Main function to orchestrate parsing, consolidation, filtering, reshaping, and saving.
    """
    print("开始整合所有Token与成本数据 (统一为USD)...")
    server_mapping = _get_simplified_server_mapping()
    
    qwen_max_data = parse_qwen_max_costs(OLD_VERSION_REPORT, server_mapping)
    pipeline_data = parse_pipeline_costs(PIPELINE_OUTPUT_DIR, server_mapping)
    
    print("\n--- (3/4) Consolidating all data ---")
    all_data = qwen_max_data + pipeline_data
    if not all_data:
        print("\n错误: 未能收集到任何成本数据。请检查路径和报告文件。")
        return
        
    df = pd.DataFrame(all_data)
    
    print("\n--- (4/4) Filtering, Reshaping, and Saving Data ---")
    
    # 1. 过滤掉非标准服务器名称的行
    valid_server_names = set(server_mapping.values())
    original_count = len(df)
    df_filtered = df[df['Server Name'].isin(valid_server_names)].copy()
    
    dropped_count = original_count - len(df_filtered)
    if dropped_count > 0:
        print(f"  - 已排除 {dropped_count} 条非标准或未映射的服务器记录。")
    else:
        print("  - 所有服务器名称均已成功标准化。")

    # 2. 创建 'Token/Cost' 显示列
    df_filtered['display_value'] = (
        df_filtered['Total Tokens'].astype(str) + '/' + 
        df_filtered['Total Cost (USD)'].round(4).astype(str)
    )

    # 3. 将表格转换为所需的宽格式
    pivot_df = df_filtered.pivot_table(
        index='Model', 
        columns='Server Name', 
        values='display_value',
        aggfunc='first' # 如有重复，使用第一个
    )
    
    # 4. 用 '0/0' 填充缺失值
    pivot_df.fillna('0/0', inplace=True)
    
    # 5. 为保证一致性，按字母顺序对列进行排序
    if not pivot_df.empty:
        sorted_columns = sorted(pivot_df.columns)
        pivot_df = pivot_df[sorted_columns]
    
    # 6. 将重塑后的数据保存到CSV (索引即为 'Model' 列，需要写入)
    pivot_df.to_csv(OUTPUT_CSV)
    
    print(f"\n数据整合完成！")
    print(f"格式化后的成本/Token数据已保存到: {OUTPUT_CSV}")
    print("\n--- 数据预览 ---")
    print(pivot_df.head())


if __name__ == "__main__":
    main() 