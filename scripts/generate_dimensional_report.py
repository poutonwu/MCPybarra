import os
import re
import glob
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

# --- Matplotlib 中文显示设置 ---
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei'] # 优先使用雅黑，如果找不到则使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 修正负号显示问题

# --- Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw_run_data')
SUMMARY_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, 'workspace')

OUTPUT_EXCEL = os.path.join(SUMMARY_DATA_DIR, "dimensional_scores_collection.xlsx")
OUTPUT_CSV = os.path.join(SUMMARY_DATA_DIR, "dimensional_scores_collection.csv")
OUTPUT_RADAR_CHART = os.path.join(RESULTS_DIR, "dimensional_radar_chart.png")

# Define input directories for all runs
QWEN_MAX_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250630_214742", "run_20250701_155804", "run_20250701_181915",
    "run_20250630_201054", "run_20250630_185156", "run_20250630_163324",
    "run_20250630_003147"
]]
PIPELINE_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250711_204700", "run_20250712_203413", "run_20250713_004043",
    "run_20250713_024028", "run_20250713_034721",
    "run_20250714_202550", "run_20250714_205741", "run_20250714_211504",
    "run_20250714_213332", "run_20250714_215025",
    "run_20250716_101039", "run_20250716_103208", "run_20250716_105214",
    "run_20250716_115725", "run_20250716_111320"
]]
METAGPT_RUNS = [os.path.join(RAW_DATA_DIR, d) for d in [
    "run_20250713_223534", "run_20250713_225157", "run_20250713_225853",
    "run_20250713_230819", "run_20250713_231639", "run_20250714_104334",
    "run_20250714_110732"
]]

# --- Mappings & Definitions ---
DIMENSIONS = ["Functionality", "Robustness", "Security", "Performance", "Transparency"]
DIMENSIONS_CN_MAP = {"功能性": "Functionality", "健壮性": "Robustness", "安全性": "Security", "性能": "Performance", "透明性": "Transparency"}
SCORE_WEIGHTS = {"功能性": 30, "健壮性": 20, "安全性": 20, "性能": 20, "透明性": 10}

def get_legend_label(model_name: str) -> str:
    """Generates a standardized legend label for a model, including its source."""
    if model_name == 'Public Baseline':
        return "(Github) Public Baseline"
    elif model_name.startswith('metaGPT-'):
        display_name = model_name.replace('metaGPT-', '')
        return f"(MetaGPT) {display_name}"
    else:
        # Assuming other models are from MCPybarra based on the user's example
        return f"(MCPybarra) {model_name}"

def get_sort_key(model_name: str) -> tuple:
    """Provides a sort key for models to ensure a consistent order."""
    if model_name == 'Public Baseline':
        return (0, model_name)  # Priority 0 for Baseline
    if 'metaGPT' in model_name:
        return (2, model_name)  # Priority 2 for MetaGPT
    return (1, model_name)      # Priority 1 for everything else (MCPybarra)

# --- Utility Functions (from consolidate_scores.py) ---

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
    """Loads pipeline_mapping.json and creates a reverse lookup map."""
    mapping_file = os.path.join(WORKSPACE_DIR, 'pipeline_mapping.json')
    reverse_mapping = {}
    if not os.path.exists(mapping_file):
        return {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        public_name = item.get('public_server_name')
        if not public_name: continue
        for model, server_info in item.get('generated_servers', {}).items():
            if server_info and 'project_name' in server_info:
                project_name = server_info['project_name']
                reverse_mapping[(model, project_name)] = public_name
    return reverse_mapping

# --- Data Parsing Functions ---

def parse_dimensional_scores_from_string(detail_str: str) -> Dict[str, float]:
    """Parses a string like '功能性: 20, 健壮性: 18' into a dict of scores."""
    scores = {}
    if not isinstance(detail_str, str):
        return {dim: 0.0 for dim in DIMENSIONS}
    
    for key_cn, key_en in DIMENSIONS_CN_MAP.items():
        match = re.search(f"{key_cn}:\s*([\d\.]+)", detail_str)
        if match:
            scores[key_en] = float(match.group(1))
        else:
            scores[key_en] = 0.0
    return scores

def parse_qwen_max_runs_detailed(run_dirs: List[str], mapping: Dict[str, str]) -> List[Dict]:
    """
    Parses the old Qwen-Max runs for detailed dimensional scores, 
    but NOW ONLY extracts Public Baseline data.
    """
    all_data = []
    # This regex now only needs to find the public server and its details column.
    table_pattern = re.compile(r'\|\s*([a-zA-Z-].*?)\s*\|.*?\|.*?\|.*?\|.*?\|\s*(.*?)\s*\|')

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        report_file_path = glob.glob(os.path.join(run_dir, "*comparison_report.md"))
        if not report_file_path:
            continue
        
        print(f"正在处理 Public Baseline (来自旧运行): {run_name}")
        with open(report_file_path[0], 'r', encoding='utf-8') as f:
            content = f.read()

        public_run_data = {'Test Subject': 'Public Baseline', 'Run Source': run_name}
        
        matches = table_pattern.findall(content)
        for row in matches:
            if '---' in row[0] or 'Public Server' in row[0]: continue
            
            # The regex captures two groups: server name and the first detail string.
            public_server, public_details_str = row[0], row[1] 
            simplified_name = _simplify_name(public_server, mapping)
            
            public_scores = parse_dimensional_scores_from_string(public_details_str)
            for dim, score in public_scores.items():
                public_run_data[f"{simplified_name}:{dim}"] = score
        
        if len(public_run_data) > 2: all_data.append(public_run_data)
            
    return all_data

def parse_pipeline_runs_detailed(run_dirs: List[str], mapping: Dict[str, str]) -> List[Dict]:
    """Parses the new pipeline runs for detailed dimensional scores."""
    all_data = []
    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        csv_path = os.path.join(run_dir, "pipeline_detailed_scores.csv")
        if not os.path.exists(csv_path): continue
            
        print(f"正在处理 Pipeline (详细) 运行: {run_name}")
        df_run = pd.read_csv(csv_path)
        # Rename 'qwen-max-latest' to 'qwen-max' to standardize model names
        df_run['model'] = df_run['model'].replace('qwen-max-latest', 'qwen-max')
        
        for model_name, group in df_run.groupby('model'):
            model_run_data = {'Test Subject': model_name, 'Run Source': run_name}
            for _, row in group.iterrows():
                simplified_name = _simplify_name(row['public_server_name'], mapping)
                for dim_cn, dim_en in DIMENSIONS_CN_MAP.items():
                    score = row.get(dim_cn, 0.0)
                    model_run_data[f"{simplified_name}:{dim_en}"] = score
            all_data.append(model_run_data)
            
    return all_data

def parse_metagpt_runs_detailed(run_dirs: List[str], reverse_mapping: Dict, simplified_name_mapping: Dict) -> List[Dict]:
    """Parses the new MetaGPT runs for detailed dimensional scores."""
    all_data = []
    score_pattern = re.compile(r"(\w+):\s*(\d+)\/\d+")

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        print(f"正在处理 MetaGPT (详细) 运行: {run_name}")
        base_path = os.path.join(run_dir, "metaGPT-servers")
        if not os.path.exists(base_path): continue

        model_dirs = [d for d in glob.glob(os.path.join(base_path, "*")) if os.path.isdir(d)]
        for model_dir in model_dirs:
            model_name = os.path.basename(model_dir)
            model_run_data = {'Test Subject': model_name, 'Run Source': run_name}
            report_files = glob.glob(os.path.join(model_dir, "detailed_report_*.md"))

            for report_path in report_files:
                filename = os.path.basename(report_path)
                prefix_to_remove = f"detailed_report_{model_name}-"
                if not filename.startswith(prefix_to_remove): continue
                
                project_name_raw = filename[len(prefix_to_remove):].replace('.md', '')
                public_server_name = reverse_mapping.get((model_name, project_name_raw))
                if not public_server_name: continue
                
                simplified_name = _simplify_name(public_server_name, simplified_name_mapping)
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                matches = score_pattern.findall(content)
                dim_scores_found = {}
                for dim_cn, score_str in matches:
                    if dim_cn in DIMENSIONS_CN_MAP:
                        dim_en = DIMENSIONS_CN_MAP[dim_cn]
                        dim_scores_found[dim_en] = float(score_str)

                # Ensure all dims are present, filling with 0 if not found
                for dim in DIMENSIONS:
                    model_run_data[f"{simplified_name}:{dim}"] = dim_scores_found.get(dim, 0.0)

            if len(model_run_data) > 2:
                all_data.append(model_run_data)
                
    return all_data

# --- Analysis Functions ---

def generate_dimensional_radar_chart(model_dimension_scores: Dict[str, pd.Series]):
    """Generates and saves the cross-dimensional radar chart."""
    print("\n--- Generating Radar Chart... ---")

    # Create a mapping from English dimension names to their weights
    weights_en = {v: SCORE_WEIGHTS[k] for k, v in DIMENSIONS_CN_MAP.items()}

    # Normalize scores based on weights using English names directly
    def normalize(dim_series):
        scores = []
        for en_dim in DIMENSIONS:
            weight = weights_en.get(en_dim, 100) # Default to 100 if not found
            score = dim_series.get(en_dim, 0)
            scores.append((score / weight) * 100 if weight > 0 else 0)
        return scores

    # Plotting logic
    labels = np.array(DIMENSIONS)
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    angles_closed = np.concatenate((angles,[angles[0]]))

    fig = plt.figure(figsize=(13, 11))
    ax = fig.add_subplot(111, polar=True)

    # Plot each model
    for model_name, dims in model_dimension_scores.items():
        if not dims.empty:
            pipeline_norm = normalize(dims)
            stats_pipeline = np.concatenate((pipeline_norm, [pipeline_norm[0]]))
            legend_label = get_legend_label(model_name)
            ax.plot(angles_closed, stats_pipeline, 'o-', linewidth=2, label=legend_label)
            ax.fill(angles_closed, stats_pipeline, alpha=0.20)

    ax.set_thetagrids(angles * 180/np.pi, labels, size=12)
    ax.tick_params(axis='x', which='major', pad=25)

    ax.set_title("Cross-Dimensional Performance Comparison (Multi-run Average)", y=1.15, size=18)
    plt.suptitle("Normalized Scores (Each dimension scaled to 100)", y=0.96, size=11, color='gray')

    ax.grid(True)
    ax.set_ylim(bottom=50)
    plt.legend(loc='upper right', bbox_to_anchor=(1.4, 1.1), fontsize=11)
    
    dim_weights_str = "Max Scores: " + ", ".join([f"{dim} ({weights_en.get(dim, 'N/A')})" for dim in DIMENSIONS])
    fig.text(0.5, 0.02, dim_weights_str, ha='center', va='bottom', size=10, color='darkred')
    
    plt.savefig(OUTPUT_RADAR_CHART, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Radar chart saved to: {OUTPUT_RADAR_CHART}")


def get_long_format_functionality_data(df_wide: pd.DataFrame) -> pd.DataFrame:
    """Converts the wide-format dataframe to a long-format one for functionality scores."""
    id_vars = ['Test Subject']
    # Filter for functionality columns only
    func_cols = [col for col in df_wide.columns if ':Functionality' in col]
    if not func_cols:
        return pd.DataFrame(columns=['Model', 'Task Name', 'Score'])
        
    df_long = df_wide.melt(id_vars=id_vars, value_vars=func_cols, var_name='Task_Dim', value_name='Score')
    
    df_long['Task Name'] = df_long['Task_Dim'].str.replace(':Functionality', '')
    df_long.rename(columns={'Test Subject': 'Model'}, inplace=True)
    
    # Exclude runs that are averages
    df_long = df_long[~df_long['Model'].str.contains('-ave')]

    # --- Load category mapping ---
    mapping_file = os.path.join(WORKSPACE_DIR, 'pipeline_mapping.json')
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            pipeline_mapping = json.load(f)
        
        # Create a reverse map from simplified_name to category
        name_to_category = {item['simplified_name']: item.get('category', 'Uncategorized') for item in pipeline_mapping}
        
        # Add category to the long format dataframe
        df_long['Category'] = df_long['Task Name'].map(name_to_category).fillna('Uncategorized')
    else:
        print("Warning: pipeline_mapping.json not found. Categories will not be added.")
        df_long['Category'] = 'Uncategorized'

    return df_long[['Model', 'Task Name', 'Score', 'Category']]


def generate_functionality_usability_report(df_long: pd.DataFrame, output_file: str):
    """Generates a text report and a stacked bar chart for functionality usability."""
    report_parts = []
    plot_data = {}
    detailed_breakdown = [] # To store data for the new markdown report
    
    report_header = """
--- Functionality Usability Analysis Report (by Average Score) ---
This report analyzes Functionality. All tasks are categorized based on their average score across all runs:
- **Perfectly Usable**: Average score between [27, 30].
- **Highly Usable**: Average score between [24, 26].
- **Partially Usable**: Average score between [18, 23].
- **Almost Unusable**: Average score below 18.
---
"""
    report_parts.append(report_header)

    models = sorted(df_long['Model'].unique())
    total_tasks = df_long['Task Name'].nunique()

    # Define categories in English for legend and data processing
    category_order = [
        "Perfectly Usable (27-30)", 
        "Highly Usable (24-26)", 
        "Partially Usable (18-23)", 
        "Almost Unusable (<18)"
    ]

    for model in models:
        model_df = df_long[df_long['Model'] == model]
        
        # Correctly calculate average score, ignoring zeros by replacing them with NaN before calculating the mean.
        # Then, fill any resulting NaNs (for tasks that only had 0 scores) back to 0.
        avg_scores = model_df.groupby('Task Name')['Score'].apply(lambda x: x.replace(0, np.nan).mean()).fillna(0)

        perfectly_usable = avg_scores[(avg_scores >= 27) & (avg_scores <= 30)]
        highly_usable = avg_scores[(avg_scores >= 24) & (avg_scores < 27)]
        partially_usable = avg_scores[(avg_scores >= 18) & (avg_scores < 24)]
        almost_unusable = avg_scores[avg_scores < 18]

        counts = {
            category_order[0]: len(perfectly_usable),
            category_order[1]: len(highly_usable),
            category_order[2]: len(partially_usable),
            category_order[3]: len(almost_unusable)
        }
        
        # Ensure that the sum of counts equals total_tasks
        if sum(counts.values()) != total_tasks:
            print(f"Warning: Task count mismatch for model '{model}'. Found {sum(counts.values())}, expected {total_tasks}.")
            
        percentages = {k: (v / total_tasks) * 100 if total_tasks > 0 else 0 for k, v in counts.items()}
        plot_data[model] = percentages

        # Create text report part (in English)
        model_report = f"### Model: {model}\n\n"
        model_report += f"**Usability Tiers (Total Tasks: {total_tasks}):**\n"
        model_report += f"- **Perfectly Usable**: {percentages[category_order[0]]:.1f}% ({counts[category_order[0]]}/{total_tasks} tasks)\n"
        model_report += f"- **Highly Usable**: {percentages[category_order[1]]:.1f}% ({counts[category_order[1]]}/{total_tasks} tasks)\n"
        model_report += f"- **Partially Usable**: {percentages[category_order[2]]:.1f}% ({counts[category_order[2]]}/{total_tasks} tasks)\n"
        model_report += f"- **Almost Unusable**: {percentages[category_order[3]]:.1f}% ({counts[category_order[3]]}/{total_tasks} tasks)\n\n"
        report_parts.append(model_report.strip() + "\n---")

        # Store detailed breakdown
        task_details = model_df.set_index('Task Name')['Category'].to_dict()

        def get_breakdown(tasks, tier_name):
            for task_name in tasks.index:
                detailed_breakdown.append({
                    'Model': model,
                    'Tier': tier_name,
                    'Task': task_name,
                    'Category': task_details.get(task_name, 'Uncategorized')
                })

        get_breakdown(perfectly_usable, category_order[0])
        get_breakdown(highly_usable, category_order[1])
        get_breakdown(partially_usable, category_order[2])
        get_breakdown(almost_unusable, category_order[3])

    # --- Generate Plot ---
    if not plot_data:
        print("Warning: No data found to generate the functionality usability chart.")
        return

    plot_df = pd.DataFrame(plot_data).T
    
    # Ensure all category columns exist, fill with 0 if not
    for cat in category_order:
        if cat not in plot_df.columns:
            plot_df[cat] = 0
    plot_df = plot_df[category_order]

    # Define a custom sort order: 1. Baseline, 2. MCPybarra, 3. Others
    model_order = sorted(plot_df.index.to_list(), key=get_sort_key)
    plot_df = plot_df.loc[model_order]
    
    # Set model names for plot index using the global helper function
    plot_df.index = [get_legend_label(name) for name in plot_df.index]

    colors = ['#4CAF50', '#8BC34A', '#FFC107', '#F44336'] # Green, Light Green, Amber, Red

    ax = plot_df.plot(
        kind='barh', 
        stacked=True, 
        color=colors, 
        figsize=(14, 8),
        width=0.75
    )

    # Add percentage labels inside the bars
    for c in ax.containers:
        labels = [f'{w:.1f}%' if w > 1 else '' for w in c.datavalues] # Hide labels for tiny segments
        ax.bar_label(c, labels=labels, label_type='center', color='white', weight='bold', fontsize=10)

    # --- Chart Styling ---
    ax.set_xlabel('Distribution of Tasks (%)', fontsize=12)
    ax.set_ylabel('')
    ax.set_title('Functionality Usability Comparison (Based on Average Score)', fontsize=16, pad=20)
    ax.tick_params(axis='y', labelsize=11)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Remove chart borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Configure legend
    ax.legend(
        title='Usability Tier', 
        bbox_to_anchor=(1.02, 1), 
        loc='upper left', 
        borderaxespad=0.,
        fontsize=11
    )
    
    chart_output_path = os.path.join(RESULTS_DIR, "functionality_usability_comparison.png")
    plt.savefig(chart_output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nFunctionality usability comparison chart saved to: {chart_output_path}")

    # --- Generate and save the new detailed breakdown report ---
    breakdown_report_path = os.path.join(RESULTS_DIR, "functionality_category_breakdown.md")
    with open(breakdown_report_path, 'w', encoding='utf-8') as f:
        f.write("# Functionality Usability Breakdown by Category\n\n")
        
        current_model = ""
        for item in sorted(detailed_breakdown, key=lambda x: (get_sort_key(x['Model'])[0], x['Model'], category_order.index(x['Tier']))):
            if item['Model'] != current_model:
                if current_model != "":
                    f.write("\n---\n\n")
                current_model = item['Model']
                f.write(f"## Model: {get_legend_label(current_model)}\n")
                current_tier = ""

            if item['Tier'] != current_tier:
                current_tier = item['Tier']
                f.write(f"\n### {current_tier}\n")
            
            f.write(f"- **Task:** {item['Task']} | **Category:** {item['Category']}\n")
            
    print(f"Detailed functionality breakdown saved to: {breakdown_report_path}")

    # Append the text report to the file
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n\n" + "\n".join(report_parts))

def generate_cross_category_usability_chart(df_long: pd.DataFrame):
    """
    Generates a faceted plot showing functionality usability breakdown across different task categories.
    """
    print("\n--- Generating Cross-Category Usability Chart... ---")
    
    # Get categories, sort them for consistent order
    categories = sorted([cat for cat in df_long['Category'].unique() if cat != 'Uncategorized'])
    num_categories = len(categories)
    if num_categories == 0:
        print("Warning: No categories found for cross-category analysis.")
        return

    # Create subplots, arranged vertically for readability
    fig, axes = plt.subplots(num_categories, 1, figsize=(14, 7 * num_categories), sharex=True)
    if num_categories == 1:
        axes = [axes]

    # Define constants for plotting
    category_order_legend = [
        "Perfectly Usable (27-30)", 
        "Highly Usable (24-26)", 
        "Partially Usable (18-23)", 
        "Almost Unusable (<18)"
    ]
    colors = ['#4CAF50', '#8BC34A', '#FFC107', '#F44336'] # Green, Light Green, Amber, Red

    # Loop through each category and create a subplot
    for i, category in enumerate(categories):
        ax = axes[i]
        category_df = df_long[df_long['Category'] == category]

        plot_data = {}
        models = sorted(category_df['Model'].unique())
        total_tasks_in_category = category_df['Task Name'].nunique()
        if total_tasks_in_category == 0:
            ax.set_title(f'Category: {category} (n=0 tasks)', fontsize=14, loc='left')
            ax.set_visible(False)
            continue

        for model in models:
            model_df = category_df[category_df['Model'] == model]
            avg_scores = model_df.groupby('Task Name')['Score'].apply(lambda x: x.replace(0, np.nan).mean()).fillna(0)
            
            perfectly_usable = avg_scores[(avg_scores >= 27) & (avg_scores <= 30)]
            highly_usable = avg_scores[(avg_scores >= 24) & (avg_scores < 27)]
            partially_usable = avg_scores[(avg_scores >= 18) & (avg_scores < 24)]
            almost_unusable = avg_scores[avg_scores < 18]

            counts = {
                category_order_legend[0]: len(perfectly_usable),
                category_order_legend[1]: len(highly_usable),
                category_order_legend[2]: len(partially_usable),
                category_order_legend[3]: len(almost_unusable)
            }
            percentages = {k: (v / total_tasks_in_category) * 100 if total_tasks_in_category > 0 else 0 for k, v in counts.items()}
            plot_data[model] = percentages

        plot_df = pd.DataFrame(plot_data).T
        for cat in category_order_legend:
            if cat not in plot_df.columns:
                plot_df[cat] = 0
        plot_df = plot_df[category_order_legend]
        
        # Sort models using the same logic
        model_order = sorted(plot_df.index.to_list(), key=get_sort_key)
        plot_df = plot_df.loc[model_order]
        plot_df.index = [get_legend_label(name) for name in plot_df.index]

        # Plotting on the subplot `ax`
        plot_df.plot(kind='barh', stacked=True, color=colors, ax=ax, width=0.8, legend=False)

        for c in ax.containers:
            labels = [f'{w:.1f}%' if w > 4 else '' for w in c.datavalues]
            ax.bar_label(c, labels=labels, label_type='center', color='white', weight='bold', fontsize=11)

        ax.set_title(f'Category: {category} (n={total_tasks_in_category} tasks)', fontsize=15, loc='left', pad=10)
        ax.tick_params(axis='y', labelsize=12)
        ax.set_ylabel('')
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.grid(axis='x', linestyle='--', alpha=0.7)

    # --- Final figure-level styling ---
    fig.suptitle('Cross-Category Functionality Usability Comparison', fontsize=20, y=1.03)
    axes[-1].set_xlabel('Distribution of Tasks (%)', fontsize=14)
    axes[-1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))
    
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, title='Usability Tier', bbox_to_anchor=(1.0, 0.95), loc='upper left', fontsize=11, title_fontsize=13)

    plt.tight_layout(rect=[0, 0, 0.88, 1]) # Adjust layout for legend

    chart_output_path = os.path.join(RESULTS_DIR, "cross_category_usability_comparison.png")
    plt.savefig(chart_output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Cross-category usability chart saved to: {chart_output_path}")


# --- Main Execution ---
def main():
    """Main function to orchestrate parsing, consolidation, and saving."""
    print("开始整合所有详细的五维分数数据...")
    server_mapping = _get_simplified_server_mapping()
    
    print("\n--- (1/3) 解析 Public Baseline (来自旧运行) 的详细数据... ---")
    baseline_data = parse_qwen_max_runs_detailed(QWEN_MAX_RUNS, server_mapping)
    
    print("\n--- (2/3) 解析 Pipeline (详细) 运行... ---")
    pipeline_data = parse_pipeline_runs_detailed(PIPELINE_RUNS, server_mapping)
    
    print("\n--- (3/3) 解析 MetaGPT (详细) 运行... ---")
    metagpt_reverse_mapping = _get_metagpt_reverse_mapping()
    metagpt_data = parse_metagpt_runs_detailed(METAGPT_RUNS, metagpt_reverse_mapping, server_mapping)
    
    all_run_data = baseline_data + pipeline_data + metagpt_data
    
    if not all_run_data:
        print("\n错误: 未能从任何来源收集到有效数据。")
        return
        
    df = pd.DataFrame(all_run_data).fillna(0)

    # --- Data Preparation for Functionality Analysis ---
    df_long_func = get_long_format_functionality_data(df)

    # --- Generate Functionality Usability Report and Chart ---
    if not df_long_func.empty:
        # Note: The second argument is the Excel file where the text report will be appended.
        generate_functionality_usability_report(df_long_func, OUTPUT_EXCEL)
        generate_cross_category_usability_chart(df_long_func)
    else:
        print("Warning: Could not extract data for functionality analysis, skipping report generation.")


    # --- 增强的统计分析与基线对比 (基于平均表现) ---
    score_cols = [col for col in df.columns if 'Test Subject' not in col and 'Run Source' not in col]

    # 1. 计算并储存基线的平均分
    baseline_df = df[df['Test Subject'] == 'Public Baseline']
    baseline_scores_nan = baseline_df[score_cols].replace(0, pd.NA)
    baseline_avg_scores = baseline_scores_nan.mean().fillna(0)

    # 2. 创建一个包含所有模型平均值的 DataFrame (纯数字)
    avg_rows_numeric = []
    for model_name in df['Test Subject'].unique():
        model_df = df[df['Test Subject'] == model_name]
        model_scores_nan = model_df[score_cols].replace(0, pd.NA)
        mean_scores = model_scores_nan.mean().fillna(0)
        
        avg_row = mean_scores.to_dict()
        avg_row['Test Subject'] = f"{model_name}-ave"
        avg_rows_numeric.append(avg_row)
    
    avg_df_numeric = pd.DataFrame(avg_rows_numeric)

    # --- A. 为机器可读的 CSV 准备数据 ---
    df_for_csv = pd.concat([df, avg_df_numeric], ignore_index=True)
    df_for_csv['model_group'] = df_for_csv['Test Subject'].str.replace('-ave', '')
    df_for_csv['is_ave'] = df_for_csv['Test Subject'].str.contains('-ave')
    df_for_csv.sort_values(by=['model_group', 'is_ave', 'Run Source'], inplace=True, na_position='last')
    
    csv_columns = ['Test Subject'] + sorted([col for col in df_for_csv.columns if ':' in col])
    final_df_csv = df_for_csv.drop(columns=['Run Source', 'model_group', 'is_ave'], errors='ignore')
    final_df_csv[csv_columns] = final_df_csv[csv_columns].round(2)
    final_df_csv = final_df_csv[csv_columns]

    # --- B. 为人类可读的 Excel 准备数据 ---
    # 3. 基于纯数字的平均值 DataFrame 创建一个用于显示的、包含字符串格式的 DataFrame
    avg_df_styled = avg_df_numeric.copy()
    avg_df_styled[score_cols] = avg_df_styled[score_cols].astype(object) # 避免类型警告
    for index, row in avg_df_styled.iterrows():
        model_avg_name = row['Test Subject']
        
        for col_name in score_cols:
            model_avg = row[col_name]
            
            if model_avg_name == 'Public Baseline-ave':
                avg_df_styled.loc[index, col_name] = f"{model_avg:.2f}"
            else:
                baseline_avg = baseline_avg_scores.get(col_name, 0)
                diff = model_avg - baseline_avg
                avg_df_styled.loc[index, col_name] = f"{model_avg:.2f} ({diff:+.2f})"

    # 4. 合并原始数据和格式化后的平均数据
    df[score_cols] = df[score_cols].round(2) # 先四舍五入原始数据
    df_combined = pd.concat([df, avg_df_styled], ignore_index=True)

    # --- 创建多级列标题 ---
    df_combined['model_group'] = df_combined['Test Subject'].str.replace('-ave', '')
    df_combined['is_ave'] = df_combined['Test Subject'].str.contains('-ave')
    df_combined.sort_values(by=['model_group', 'is_ave', 'Run Source'], inplace=True, na_position='last')
    
    final_df = df_combined.drop(columns=['Run Source', 'model_group', 'is_ave'], errors='ignore')
    
    # 解析列名
    column_tuples = []
    for col in final_df.columns:
        if col == 'Test Subject':
            column_tuples.append((col, ''))
        else:
            parts = col.split(':', 1)
            column_tuples.append((parts[0], parts[1]))
    
    final_df.columns = pd.MultiIndex.from_tuples(column_tuples)

    # 按任务名和维度排序
    sorted_tasks = sorted(list(set(parts[0] for parts in column_tuples if parts[0] != 'Test Subject')))
    
    final_column_order = [('Test Subject', '')]
    for task in sorted_tasks:
        for dim in DIMENSIONS:
            if (task, dim) in final_df.columns:
                final_column_order.append((task, dim))
    
    final_df = final_df[final_column_order]

    # --- C. 为雷达图准备数据并生成图像 ---
    model_avg_dims = {}
    avg_df_for_radar = avg_df_numeric.set_index('Test Subject')

    for model_name_raw, row in avg_df_for_radar.iterrows():
        model_name = model_name_raw.replace('-ave', '')
        
        dim_scores = {}
        for dim_en in DIMENSIONS:
            # Select all columns for the current dimension (e.g., all ending with ':Functionality')
            dim_cols = [col for col in avg_df_for_radar.columns if col.endswith(f":{dim_en}")]
            
            # Get average scores for each task. To ignore 0-score tasks in the final dimension
            # average, replace 0 with NaN before calculating the mean.
            task_avg_scores = row[dim_cols]
            dim_scores[dim_en] = task_avg_scores.replace(0, np.nan).mean()
            
        # Create the final Series for the model, filling any potential NaN with 0
        # (e.g., if a model scored 0 on all tasks for a specific dimension)
        model_avg_dims[model_name] = pd.Series(dim_scores).fillna(0)

    generate_dimensional_radar_chart(model_avg_dims)

    # --- D. 保存文件 ---
    # 保存到 Excel
    final_df.to_excel(OUTPUT_EXCEL, index=True)

    # 新增：保存到 CSV
    final_df_csv.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print(f"\n数据整合完成！共找到 {len(df_combined)} 条记录。")
    print(f"包含统计数据的详细维度报告已保存到: {OUTPUT_EXCEL}")
    print(f"机器可读的维度报告已保存到: {OUTPUT_CSV}")


if __name__ == "__main__":
    main() 