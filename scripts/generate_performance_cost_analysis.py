import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# --- Matplotlib & Seaborn Configuration ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

# --- File & Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

# Note: 'average_usage_report.md' is not a standard data file. Ensure it exists in the data directory.
USAGE_REPORT_PATH = os.path.join(DATA_DIR, 'average_usage_report.md')
SCORES_PATH = os.path.join(DATA_DIR, 'raw_scores_collection.csv')
PUBLIC_COMPARISON_PATH = os.path.join(DATA_DIR, 'average_comparison_data.csv')
CHART_OUTPUT_PATH = os.path.join(RESULTS_DIR, 'performance_cost_analysis.png')
REPORT_OUTPUT_PATH = os.path.join(RESULTS_DIR, 'performance_cost_analysis_report.md')

def parse_usage_report(report_path):
    """Parses cost and token data from the usage report markdown file."""
    if not os.path.exists(report_path):
        print(f"Error: Usage report not found at '{report_path}'")
        return pd.DataFrame()
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    data = []
    
    table_started = False
    for line in lines:
        if '|---' in line:
            table_started = True
            continue
        if not table_started or not line.strip() or '说明' in line or '各模型' in line:
            continue
            
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) == 3:
            model_name = parts[0].lower().replace('_', '-')

            # Skip the old 'qwen-max' entry to avoid duplicates, as it's replaced by 'qwen-max-latest'.
            if model_name == 'qwen-max':
                continue

            if 'qwen-max-latest' in model_name:
                model_name = 'qwen-max'

            cost_str = parts[1]
            tokens_str = parts[2]
            
            cost = float(re.sub(r'[^\d.]', '', cost_str))
            tokens = int(re.sub(r'[^\d]', '', tokens_str))
            
            data.append({
                "model": model_name,
                "avg_cost_usd": cost,
                "avg_tokens": tokens
            })
            
    return pd.DataFrame(data)

def calculate_average_scores(scores_path):
    """Calculates average scores from the scores csv file."""
    df = pd.read_csv(scores_path)
    
    avg_scores = df.drop(columns=['public_server_name']).mean().reset_index()
    avg_scores.columns = ['model', 'avg_score']
    
    return avg_scores

def calculate_pipeline_scores(scores_path):
    """
    Calculates average scores for pipeline models from raw_scores_collection.csv.
    This function specifically targets rows with '-ave' to get summary scores.
    """
    df = pd.read_csv(scores_path)
    
    # Map raw model names from CSV to the names used in the cost report
    model_mapping = {
        'gpt-4o-ave': 'gpt-4o',
        'gemini-2.5-pro-ave': 'gemini-2.5-pro',
        'qwen-plus-ave': 'qwen-plus',
        'qwen-max-latest-ave': 'qwen-max',
        'deepseek-v3-ave': 'deepseek-v3',
    }
    
    avg_scores_data = []
    
    # Filter for the summary rows ('-ave')
    summary_df = df[df['Test Subject'].isin(model_mapping.keys())]
    
    for _, row in summary_df.iterrows():
        raw_model_name = row['Test Subject']
        model_name = model_mapping[raw_model_name]
        avg_score = row['Average score']
        avg_scores_data.append({'model': model_name, 'avg_score': avg_score})
            
    return pd.DataFrame(avg_scores_data)


def generate_bubble_chart(df, output_path, baseline_score):
    """Generate the performance-cost bubble chart with a clear, separate legend and baseline."""
    plt.style.use('seaborn-v0_8-whitegrid')
    # Use a wider figure for side-by-side plots, sharing the Y-axis
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(20, 12), sharey=True, gridspec_kw={'wspace': 0.1})
    fig.suptitle('Performance vs. Cost Analysis', fontsize=32, y=0.98)

    # Define a cost threshold to split the data into two groups
    cost_threshold = 0.055
    df_low_cost = df[df['avg_cost_usd'] < cost_threshold]
    df_high_cost = df[df['avg_cost_usd'] >= cost_threshold]
    
    mean_score = df['avg_score'].mean()

    # Define a common function to plot data points on an axis to avoid code duplication
    def plot_data(ax, data, is_left_plot):
        if data.empty:
            ax.set_visible(False)
            return

        # 统一使用普通刻度而非对数刻度
        # ax.set_xscale('log')
        
        model_colors = {
            'gpt-4o': '#1f77b4',           # Muted Blue
            'gemini-2.5-pro': '#ff7f0e',   # Safety Orange
            'qwen-plus': '#2ca02c',        # Cooked Asparagus Green
            'qwen-max': '#d62728',        # Brick Red
            'deepseek-v3': '#9467bd',      # Muted Purple
        }
        colors = data['model'].map(model_colors)

        min_bubble_size, max_bubble_size = 300, 1800
        min_tokens, max_tokens = df['avg_tokens'].min(), df['avg_tokens'].max()
        if max_tokens - min_tokens > 0:
            size = min_bubble_size + ((data['avg_tokens'] - min_tokens) / (max_tokens - min_tokens)) * (max_bubble_size - min_bubble_size)
        else:
            size = [min_bubble_size] * len(data)

        ax.scatter(data['avg_cost_usd'], data['avg_score'], s=size, alpha=0.7, c=colors)

        for _, row in data.iterrows():
            # Apply specific label placement rules for challenging points
            model_name = row['model']
            if model_name == 'gemini-2.5-pro':
                # Place above to avoid subplot overlap
                ha, va = 'center', 'bottom'
                x_offset, y_offset = 1.005, 0.1
            elif model_name == 'gpt-4o':
                # Place below to avoid the right edge
                ha, va = 'center', 'top'
                x_offset, y_offset = 1.0, 0.22 # Centered horizontally, with a negative y-offset to move it down
            else:
                # Default: place to the right
                ha, va = 'left', 'center'
                x_offset, y_offset = 1.02, 0

            ax.text(row['avg_cost_usd'] * x_offset, row['avg_score'] + y_offset, row['model'].upper(),
                    verticalalignment=va, horizontalalignment=ha, fontsize=18, weight='bold')

        # Shared horizontal lines
        ax.axhline(mean_score, color='grey', linestyle='--', linewidth=1)
        if baseline_score is not None:
            ax.axhline(baseline_score, color='dodgerblue', linestyle=':', linewidth=2.5)
            # Add baseline label only once on the right plot for clarity
            if not is_left_plot:
                ax.text(ax.get_xlim()[1], baseline_score, '  Public Servers Avg Score  ',
                        va='center', ha='right', color='dodgerblue', fontsize=22, weight='bold',
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0))

    # --- Plot on both subplots ---
    plot_data(ax_left, df_low_cost, is_left_plot=True)
    plot_data(ax_right, df_high_cost, is_left_plot=False)
    
    # --- 设置固定的x轴范围和刻度，确保左右两图对齐 ---
    # 左侧图表范围
    ax_left.set_xlim(0.015, 0.045)
    # 右侧图表范围
    ax_right.set_xlim(0.13, 0.145)
    
    # 设置刻度标签格式和大小
    for ax in [ax_left, ax_right]:
        # 增大刻度标签字体
        ax.tick_params(axis='both', which='major', labelsize=16)
        # 设置x轴标签格式
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.3f}'))

    # --- Set titles, labels, and quadrant text for each subplot ---
    zone_props = {'fontsize': 16, 'ha': 'center', 'va': 'center', 'alpha': 0.6}
    
    # Left plot: Low Cost
    ax_left.set_title("Low Cost Models", fontsize=24, pad=20)
    ax_left.text(0.5, 0.65, 'High Score, Low Cost\n(Star Zone)', color='green', transform=ax_left.transAxes, **zone_props)
    ax_left.text(0.5, 0.1, 'Low Score, Low Cost\n(Economic Zone)', color='grey', transform=ax_left.transAxes, **zone_props)
    
    # Right plot: High Cost
    ax_right.set_title("High Cost Models", fontsize=24, pad=20)
    ax_right.text(0.5, 0.65, 'High Score, High Cost\n(Performance Zone)', color='grey', transform=ax_right.transAxes, **zone_props)
    ax_right.text(0.5, 0.1, 'Low Score, High Cost\n(Warning Zone)', color='red', transform=ax_right.transAxes, **zone_props)

    # --- Common Axis Labels ---
    fig.supxlabel('Average Project Cost (USD) - Lower is Better →', fontsize=26, y=0.05)
    fig.supylabel('Average Performance Score - Higher is Better →', fontsize=26, x=0.08)
    
    # --- Create Legend and place it completely outside the plot area ---
    legend_handles = []
    token_values = sorted(list(df['avg_tokens'].unique()))
    if len(token_values) > 3:
        token_values = [min(token_values), np.median(token_values), max(token_values)]
    labels = [f"{int(v/1000)}k Tokens" for v in token_values]
    
    legend_bubble_sizes = np.linspace(50, 300, len(labels))
    for size, label in zip(legend_bubble_sizes, labels):
        legend_handles.append(plt.scatter([], [], s=size, c='gray', alpha=0.6, label=label))
    
    # Place legend to the right of the figure, completely outside the subplots
    fig.legend(handles=legend_handles, title='Avg Token Consumption', loc='upper left', bbox_to_anchor=(0.81, 0.89),
               labelspacing=2.5, borderpad=1.2, frameon=True, framealpha=0.7, fontsize=18, title_fontsize=20)

    # Adjust main figure layout to make even more space for the legend on the right.
    fig.subplots_adjust(right=0.80)
    
    plt.savefig(output_path, dpi=500)
    plt.close(fig)
    print(f"Chart saved to: {output_path}")

def generate_report(df, output_path):
    """Generate the Markdown analysis report."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Performance vs. Cost Analysis Report\n\n")
        f.write("This report provides a multi-dimensional evaluation of models based on their performance scores, project costs, and token consumption.\n\n")
        
        f.write("## Data Summary\n\n")
        report_df = df.copy()
        report_df.rename(columns={
            'model': 'Model',
            'avg_score': 'Average Score',
            'avg_cost_usd': 'Average Cost (USD)',
            'avg_tokens': 'Average Tokens'
        }, inplace=True)
        f.write(report_df.to_markdown(index=False))
        
        f.write("\n\n## Chart Interpretation\n\n")
        f.write("The following bubble chart visualizes the analysis, where:\n")
        f.write("- **X-axis**: Average Project Cost (USD) - Further to the left is better.\n")
        f.write("- **Y-axis**: Average Performance Score - Higher is better.\n")
        f.write("- **Bubble Size**: Average Token Consumption - Smaller is better.\n\n")
        f.write("![Performance vs. Cost Analysis](performance_cost_analysis.png)\n\n")
        f.write("### Quadrant Analysis\n\n")
        f.write("- **Top-Left (Star Zone)**: High performance at a low cost. This is the ideal quadrant.\n")
        f.write("- **Top-Right (Performance Zone)**: High performance at a high cost. Models are effective but expensive.\n")
        f.write("- **Bottom-Left (Economic Zone)**: Low performance at a low cost. Suitable for budget-sensitive applications where performance is not critical.\n")
        f.write("- **Bottom-Right (Warning Zone)**: Low performance at a high cost. This is the least desirable quadrant.\n")

    print(f"Report saved to: {output_path}")

def main():
    print(f"Parsing cost data from '{USAGE_REPORT_PATH}'...")
    df_cost = parse_usage_report(USAGE_REPORT_PATH)
    if df_cost.empty:
        print("Could not proceed without cost data.")
        return

    print(f"Calculating average scores from '{SCORES_PATH}'...")
    df_scores = calculate_pipeline_scores(SCORES_PATH)
    
    public_baseline_score = None
    if os.path.exists(PUBLIC_COMPARISON_PATH):
        print(f"Calculating Public Baseline score from '{PUBLIC_COMPARISON_PATH}'...")
        df_public = pd.read_csv(PUBLIC_COMPARISON_PATH)
        public_baseline_score = df_public['Public Score'].mean()
    else:
        print(f"Warning: Public comparison data not found at '{PUBLIC_COMPARISON_PATH}'. Baseline will be skipped.")

    print("\nMerging data...")
    df_final = pd.merge(df_scores, df_cost, on='model', how='inner')

    if df_final.empty:
        print("\nError: Final data is empty! Check if model names match in the source files.")
        return

    df_final['avg_score'] = df_final['avg_score'].round(2)
    df_final['avg_cost_usd'] = df_final['avg_cost_usd'].round(4)
    df_final['avg_tokens'] = df_final['avg_tokens'].astype(int)
    
    print("\n--- Final Merged Data ---\n")
    print(df_final)
    if public_baseline_score is not None:
        print(f"\nPublic Baseline Score: {public_baseline_score:.2f}")
    print("\n---------------------\n")

    generate_bubble_chart(df_final, CHART_OUTPUT_PATH, public_baseline_score)
    generate_report(df_final, REPORT_OUTPUT_PATH)
    
    print("Analysis complete!")

if __name__ == '__main__':
    main() 