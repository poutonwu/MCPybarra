import os
import re
import pandas as pd

# --- Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, 'workspace')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')

# Input paths
PIPELINE_OUTPUT_BASE_DIR = os.path.join(WORKSPACE_DIR, 'pipeline-output-servers')
OLD_REPORT_PATH = os.path.join(DATA_DIR, 'old_version_token_consumption_report.md')

# Output path
OUTPUT_REPORT_PATH = os.path.join(DATA_DIR, 'average_usage_report.md')


def calculate_usage_statistics():
    """
    遍历指定模型的项目目录，读取每个项目的 'statistics_report.md'，
    解析出 'Total Tokens' 和 '总预估成本 (RMB)'，并计算每个模型的平均消耗。
    """
    base_dir = PIPELINE_OUTPUT_BASE_DIR
    
    models = ['gpt-4o', 'qwen-plus', 'qwen-max-latest', 'gemini-2.5-pro', 'deepseek-v3']
    results = {}
    
    print(f"开始分析, 基础目录: {base_dir}")

    for model in models:
        model_path = os.path.join(base_dir, model)
        if not os.path.isdir(model_path):
            print(f"警告: 模型目录 '{model}' 未在 '{model_path}' 找到。跳过。")
            continue

        total_tokens = 0
        total_cost = 0.0
        project_count = 0
        
        print(f"\n--- 正在处理模型: {model.upper()} ---")
        
        try:
            projects = [d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))]
        except FileNotFoundError:
            print(f"警告: 无法读取模型目录 '{model_path}'。跳过。")
            continue

        for project in projects:
            project_path = os.path.join(model_path, project)
            
            possible_report_paths = [
                os.path.join(project_path, 'statistics_report.md'),
                os.path.join(project_path, 'refined', 'statistics_report.md')
            ]
            
            report_found = False
            for report_path in possible_report_paths:
                if os.path.exists(report_path):
                    report_found = True
                    try:
                        with open(report_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # 使用 findall 查找所有模型的成本和 Token
                        model_usage_pattern = re.compile(
                            r"### 模型: `(.+?)`.*?"
                            r"\|\s*\*\*总成本\s*\(RMB\)\*\*\s*\|\s*\*\*¥([\d,.]+)\*\*\s*\|.*?"
                            r"\|\s*总 Token\s*\|\s*([\d,]+)\s*\|",
                            re.DOTALL | re.IGNORECASE
                        )
                        
                        matches = model_usage_pattern.findall(content)
                        
                        if matches:
                            project_total_tokens = 0
                            project_total_cost_usd = 0.0 # Changed to USD
                            
                            for model_name, cost_str, tokens_str in matches:
                                tokens = int(tokens_str.replace(',', ''))
                                cost_rmb = float(cost_str.replace(',', ''))
                                
                                # Convert cost to USD
                                if model == 'gemini-2.5-pro' and 'gemini-2.5-pro' in model_name:
                                    cost_rmb *= 7.2
                                cost_usd = cost_rmb / 7.2
                                
                                project_total_tokens += tokens
                                project_total_cost_usd += cost_usd
                            
                            total_tokens += project_total_tokens
                            total_cost += project_total_cost_usd # Accumulate USD cost
                            project_count += 1
                            print(f"  - 找到 {project_total_tokens} tokens, ${project_total_cost_usd:.4f} 在 '{os.path.relpath(report_path, base_dir)}'")
                        else:
                            # Fallback for old reports with only total tokens/cost
                            total_tokens_pattern = re.search(r"Total Token Consumption\*\* \| \*\*([\d,]+)\*\*", content)
                            total_cost_pattern = re.search(r"Total Estimated Cost \(RMB\)\*\* \| \*\*¥([\d,.]+)\*\*", content)

                            if total_tokens_pattern and total_cost_pattern:
                                project_total_tokens = int(total_tokens_pattern.group(1).replace(',', ''))
                                project_total_cost_rmb = float(total_cost_pattern.group(1).replace(',', ''))
                                
                                # Convert cost to USD, applying Gemini-specific correction if needed
                                cost_usd = project_total_cost_rmb / 7.2
                                
                                total_tokens += project_total_tokens
                                total_cost += cost_usd # Accumulate USD cost
                                project_count += 1
                                print(f"  - (回退) 找到 {project_total_tokens} tokens, ${cost_usd:.4f} 在 '{os.path.relpath(report_path, base_dir)}'")
                            else:
                                print(f"  - 警告: 在 '{os.path.relpath(report_path, base_dir)}' 中未找到模型使用情况或总消耗。")

                    except Exception as e:
                        print(f"  - 错误: 处理 '{os.path.relpath(report_path, base_dir)}' 时出错: {e}。")
                    
                    break
            
            if not report_found:
                print(f"  - 信息: 在项目 '{project}' 中未找到 'statistics_report.md'。")

        if project_count > 0:
            average_tokens = total_tokens / project_count
            average_cost_usd = total_cost / project_count
            results[model] = {
                "total_tokens": total_tokens,
                "total_cost": total_cost, # Already in USD
                "project_count": project_count,
                "average_tokens": average_tokens,
                "average_cost": average_cost_usd
            }
        else:
            results[model] = { "total_tokens": 0, "total_cost": 0.0, "project_count": 0, "average_tokens": 0, "average_cost": 0.0 }

    # --- 处理旧版本报告 ---
    old_report_path = OLD_REPORT_PATH
    if os.path.exists(old_report_path):
        print("\n--- 正在处理旧版本报告: QWEN-MAX ---")
        try:
            with open(old_report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            qwen_max_prices = {
                "prompt": 0.0000024 / 7.2,  # USD per token from config
                "completion": 0.0000096 / 7.2  # USD per token from config
            }

            old_total_tokens = 0
            old_total_cost_usd = 0.0
            old_project_count = 0

            project_total_lines = re.findall(r'\|\s*\*\*Project Total\*\*.*', content)

            for line in project_total_lines:
                parts = line.split('|')
                if len(parts) > 5:
                    prompt_tokens_str = parts[2].strip()
                    completion_tokens_str = parts[3].strip()
                    total_tokens_str = parts[4].strip()
                    
                    prompt_tokens = int(re.sub(r'[^\d]', '', prompt_tokens_str))
                    completion_tokens = int(re.sub(r'[^\d]', '', completion_tokens_str))
                    total_tokens = int(re.sub(r'[^\d]', '', total_tokens_str))
                    
                    # Recalculate cost in USD based on token counts and new rates
                    cost_usd = (prompt_tokens * qwen_max_prices["prompt"]) + \
                               (completion_tokens * qwen_max_prices["completion"])
                    
                    old_total_tokens += total_tokens
                    old_total_cost_usd += cost_usd
                    old_project_count += 1
            
            if old_project_count > 0:
                average_tokens = old_total_tokens / old_project_count
                average_cost_usd = old_total_cost_usd / old_project_count
                results['QWEN-MAX'] = {
                    "average_tokens": average_tokens,
                    "average_cost": average_cost_usd
                }
                print(f"  - 找到 {old_project_count} 个项目")
                print(f"  - 平均项目成本: ${average_cost_usd:.4f} (按QWEN-MAX费率重新计算)")
                print(f"  - 平均Token用量: {average_tokens:.0f}")

        except Exception as e:
            print(f"  - 错误: 处理旧版本报告时出错: {e}")


    # --- 输出结果 ---
    print("\n\n--- 平均Token与成本消耗总结 (USD) ---")
    
    report_file_path = OUTPUT_REPORT_PATH
    
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write("# 各模型平均Token与成本消耗报告 (USD)\n\n")
        f.write("| 模型 | 平均项目成本 (USD) | 平均Token用量 (每个项目) |\n")
        f.write("|---|---|---|\n")

        sorted_results = sorted(results.items(), key=lambda item: item[1]['average_cost'], reverse=True)

        for model, data in sorted_results:
            print(f"模型: {model.upper()}")
            print(f"  - 平均项目成本: ${data['average_cost']:.4f}")
            print(f"  - 平均Token用量: {data['average_tokens']:.0f}")
            f.write(f"| {model.upper()} | ${data['average_cost']:.4f} | {data['average_tokens']:.0f} |\n")

        f.write("\n---\n\n")
        f.write("### 说明\n\n")
        f.write("上述数据反映了使用不同主要模型生成一个完整项目所需的总开销。在此工作流中，**主要模型**（如 GPT-4O, Gemini-2.5-Pro）仅用于初始的**代码生成**阶段。后续的**测试**和**代码精炼**阶段，则统一使用 **Qwen-Plus** 模型。因此，每个项目的总成本是其主要生成模型与 Qwen-Plus 模型共同作用的结果。")

    print(f"\n总结报告已保存至: '{report_file_path}'")

if __name__ == "__main__":
    calculate_usage_statistics() 