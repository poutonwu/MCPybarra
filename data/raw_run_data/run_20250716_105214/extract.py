import json
import os
import pandas as pd
import re
from io import StringIO

def _simplify_public_name(name: str) -> str:
    """Simplifies the public server name for better readability on charts using a specific mapping."""
    name = name.lower()
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

def parse_dimension_scores(file_path: str) -> dict:
    """Parses the <SCORES> block from a detailed report file."""
    scores = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scores_match = re.search(r'<SCORES>(.*?)</SCORES>', content, re.S)
        if scores_match:
            scores_text = scores_match.group(1).strip()
            for line in scores_text.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip()
                    # We only want the score, not the max value (e.g., '30/30' -> 30)
                    score_val = val.split('/')[0].strip()
                    if key != '总分': # Exclude total score
                        scores[key] = int(score_val)
    except Exception as e:
        print(f"Error parsing dimension scores from {file_path}: {e}")
    return scores

def run():
    """
    Reads data from benchmark_summary.json, combines it with the existing scores in
    pipeline_comparison_report.md, and writes the completed report back to the file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    summary_json_path = os.path.join(script_dir, 'pipeline_server_tests/benchmark_summary.json')
    report_md_path = os.path.join(script_dir, 'pipeline_server_tests/pipeline_comparison_report.md')
    mapping_json_path = os.path.abspath(os.path.join(script_dir, '..', '..', 'workspace/pipeline_mapping.json'))

    print("Loading data...")
    with open(summary_json_path, 'r', encoding='utf-8') as f:
        summary_list = json.load(f)
    with open(mapping_json_path, 'r', encoding='utf-8') as f:
        mapping_list = json.load(f)
    with open(report_md_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    print("Data loaded successfully.")

    report_key_to_public_name = {}
    for server_info in mapping_list:
        public_name_raw = server_info.get("public_server_name")
        if not public_name_raw:
            continue
        simplified_public_name = _simplify_public_name(public_name_raw)
        generated_servers = server_info.get("generated_servers", {})
        for model_name, server_details in generated_servers.items():
            if server_details and server_details.get("project_name"):
                project_name = server_details["project_name"]
                report_key = f"{model_name}-{project_name}"
                report_key_to_public_name[report_key] = simplified_public_name

    # --- Extract and save detailed dimension scores ---
    print("\nExtracting detailed dimension scores...")
    detailed_scores_data = []
    tests_dir = os.path.join(script_dir, 'pipeline_server_tests')
    model_dirs = [d for d in os.listdir(tests_dir) if os.path.isdir(os.path.join(tests_dir, d)) and d in ["gemini-2.5-pro", "gpt-4o", "qwen-max-latest", "qwen-plus", "deepseek-v3", "deepseek-r1-0528"]]
    
    for model_dir in model_dirs:
        model_path = os.path.join(tests_dir, model_dir)
        for report_filename in os.listdir(model_path):
            if report_filename.startswith('detailed_report_') and report_filename.endswith('.md'):
                report_key = report_filename.replace('detailed_report_', '').replace('.md', '')
                public_name = report_key_to_public_name.get(report_key)
                
                if not public_name:
                    print(f"Warning: Could not find public name for report key '{report_key}'. Skipping.")
                    continue
                
                file_path = os.path.join(model_path, report_filename)
                dim_scores = parse_dimension_scores(file_path)
                
                if dim_scores:
                    record = {
                        'public_server_name': public_name,
                        'model': model_dir,
                    }
                    record.update(dim_scores)
                    detailed_scores_data.append(record)

    if detailed_scores_data:
        detailed_scores_df = pd.DataFrame(detailed_scores_data)
        detailed_scores_csv_path = os.path.join(script_dir, 'pipeline_detailed_scores.csv')
        
        # Ensure consistent column order
        cols_order = ['public_server_name', 'model', '功能性', '健壮性', '安全性', '性能', '透明性']
        existing_cols = [c for c in cols_order if c in detailed_scores_df.columns]
        detailed_scores_df = detailed_scores_df[existing_cols]
        
        detailed_scores_df.to_csv(detailed_scores_csv_path, index=False, encoding='utf-8-sig')
        print(f"Successfully generated detailed scores CSV: {detailed_scores_csv_path}")
    else:
        print("Warning: No detailed dimension scores were extracted.")
    # --- End of dimension score extraction ---

    data_to_fill = {'duration': {}, 'tokens': {}}
    for summary_entry in summary_list:
        benchmark_results = summary_entry.get("benchmark_results", {})
        for report_key, result_data in benchmark_results.items():
            public_name = report_key_to_public_name.get(report_key)
            model_name = next((m for m in ["gemini-2.5-pro", "gpt-4o", "qwen-plus"] if m in report_key), None)
            if not public_name or not model_name:
                continue
            suite_summary = result_data.get("suite_summary", {})
            if public_name not in data_to_fill['duration']:
                data_to_fill['duration'][public_name] = {}
                data_to_fill['tokens'][public_name] = {}
            data_to_fill['duration'][public_name][model_name] = suite_summary.get("total_duration", 0)
            data_to_fill['tokens'][public_name][model_name] = suite_summary.get("total_llm_tokens", 0)
    print("Processed summary data.")

    score_table_match = re.search(r'(## 1\. Overall Score Comparison.*?\n\n.*?)(\n\n##|\Z)', report_content, re.S)
    if not score_table_match:
        raise ValueError("Could not find the score table in the report.")
    
    score_section_content = score_table_match.group(1)
    score_table_md = score_section_content.split('\n\n', 1)[1].strip()

    lines = [line.strip() for line in score_table_md.split('\n') if line.strip() and not line.strip().startswith('|:--')]
    header = [h.strip() for h in lines[0].strip('|').split('|')]
    data = [[d.strip() for d in row.strip('|').split('|')] for row in lines[1:]]
    scores_df = pd.DataFrame(data, columns=header).set_index(header[0])
    server_names = [name for name in scores_df.index if not name.startswith('**')]
    model_names = scores_df.columns.tolist()

    duration_df = pd.DataFrame(index=server_names, columns=model_names, dtype=float)
    tokens_df = pd.DataFrame(index=server_names, columns=model_names, dtype=float)

    for server in server_names:
        for model in model_names:
            duration_df.loc[server, model] = data_to_fill.get('duration', {}).get(server, {}).get(model, 0)
            tokens_df.loc[server, model] = data_to_fill.get('tokens', {}).get(server, {}).get(model, 0)
    
    duration_df.loc['**Total Duration**'] = duration_df.sum()
    tokens_df.loc['**Total Tokens**'] = tokens_df.sum().astype(int)

    duration_df.index.name = scores_df.index.name
    tokens_df.index.name = scores_df.index.name
    print("Created new data tables for duration and tokens.")

    duration_table_new_md = duration_df.to_markdown(floatfmt=".2f")
    tokens_table_new_md = tokens_df.to_markdown()

    # Reconstruct the report
    report_intro = report_content.split('## 1.')[0]
    
    new_report_content = (
        f"{report_intro.strip()}\n\n"
        f"## 1. Overall Score Comparison (Higher is Better)\n\n{score_table_md}\n\n"
        f"## 2. Total Duration Comparison (in seconds, Lower is Better)\n\n{duration_table_new_md}\n\n"
        f"## 3. Total Token Consumption (Lower is Better)\n\n{tokens_table_new_md}\n"
    )

    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write(new_report_content)
    print(f"Successfully updated report: {report_md_path}")

if __name__ == '__main__':
    run()
