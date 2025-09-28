import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Matplotlib & Seaborn Configuration ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

# --- File & Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

RAW_SCORES_PATH = os.path.join(DATA_DIR, 'raw_scores_collection.csv')
CHART_OUTPUT_PATH = os.path.join(RESULTS_DIR, 'overall_performance_comparison.png')
REPORT_OUTPUT_PATH = os.path.join(RESULTS_DIR, 'overall_performance_report.md')

def load_and_prepare_data(csv_path):
    """Loads and prepares data from the raw scores collection for plotting."""
    df = pd.read_csv(csv_path)
    
    def parse_score(score):
        """Extracts the leading float from a string like '88.00 (+0.00)'."""
        if isinstance(score, str):
            match = re.search(r'^-?(\d+\.\d+|\d+)', score)
            if match:
                return float(match.group(0))
        if isinstance(score, (int, float)):
            return float(score)
        return np.nan

    start_col_index = df.columns.get_loc('Test Subject') + 1
    end_col_index = df.columns.get_loc('Average score')
    score_cols = df.columns[start_col_index:end_col_index]

    for col in score_cols:
        df[col] = df[col].apply(parse_score)

    df.set_index('Test Subject', inplace=True)
    
    baseline_scores = df.loc['Public Baseline-ave', score_cols]

    mcpybarra_models = [
        'gemini-2.5-pro-ave',
        'gpt-4o-ave',
        'qwen-plus-ave',
        'deepseek-v3-ave',
        'qwen-max-latest-ave'
    ]
    mcpybarra_models_present = [model for model in mcpybarra_models if model in df.index]
    mcpybarra_scores = df.loc[mcpybarra_models_present, score_cols].max()

    metagpt_scores = df.loc['metaGPT-qwen-plus-ave', score_cols]

    plot_df = pd.DataFrame({
        'Simplified Name': score_cols,
        'Public Score': baseline_scores.values,
        'Best of MCPybarra': mcpybarra_scores.values,
        'Best of MetaGPT': metagpt_scores.values
    })

    plot_df['MCPybarra Improvement'] = plot_df['Best of MCPybarra'] - plot_df['Public Score']
    plot_df['MetaGPT Improvement'] = plot_df['Best of MetaGPT'] - plot_df['Public Score']
    
    plot_df.sort_values('MCPybarra Improvement', ascending=False, inplace=True)
    
    return plot_df

def generate_chart(df, output_path):
    """Generates and saves the comparison chart."""
    fig, ax1 = plt.subplots(figsize=(24, 14))
    
    simplified_names = df['Simplified Name']
    x = np.arange(len(simplified_names))
    width = 0.28
    
    colors = {'Public Baseline': '#2ca02c', 'MCPybarra': '#1f77b4', 'MetaGPT': '#ff7f0e'}

    # Top Panel: Score Comparison
    rects1 = ax1.bar(x - width, df['Public Score'], width, label='Public Baseline', color=colors['Public Baseline'])
    rects2 = ax1.bar(x, df['Best of MCPybarra'], width, label='MCPybarra', color=colors['MCPybarra'])
    rects3 = ax1.bar(x + width, df['Best of MetaGPT'], width, label='MetaGPT', color=colors['MetaGPT'])
    
    ax1.set_ylabel('Total Score', fontsize=18)
    ax1.set_title('Best of MCPybarra vs. MetaGPT vs. Public Baseline', fontsize=22)
    ax1.set_xticks(x)
    ax1.set_xticklabels(simplified_names, rotation=45, ha='right', fontsize=14)
    ax1.legend(fontsize=16)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    max_score = max(df['Public Score'].max(), df['Best of MCPybarra'].max(), df['Best of MetaGPT'].max())
    ax1.set_ylim(0, max_score * 1.15)

    ax1.bar_label(rects1, fmt='%.1f', padding=3, fontsize=12)
    ax1.bar_label(rects2, fmt='%.1f', padding=3, fontsize=12)
    ax1.bar_label(rects3, fmt='%.1f', padding=3, fontsize=12)

    fig.tight_layout(pad=3.0)
    plt.savefig(output_path, dpi=500)
    plt.close(fig)
    print(f"Chart saved to: {output_path}")

def generate_horizontal_chart(df, output_path):
    """Generates a two-column horizontal bar chart to save space and improve readability."""
    # Split dataframe for two columns
    n_items = len(df)
    split_point = (n_items + 1) // 2
    df1 = df.iloc[:split_point]
    df2 = df.iloc[split_point:]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 15), sharey=False)
    fig.suptitle('Best of MCPybarra Consistently Outperforms Human and MetaGPT Baselines', fontsize=30, y=0.96)
    
    width = 0.28
    colors = {'Public Baseline': '#2ca02c', 'MCPybarra': '#1f77b4', 'MetaGPT': '#ff7f0e'}

    def plot_subplot(ax, data):
        simplified_names = data['Simplified Name']
        y = np.arange(len(simplified_names))
        
        # New order: MCPybarra (top), Public Baseline (middle), MetaGPT (bottom)
        # With invert_yaxis(), the logic is reversed: lower y values appear higher on the plot.
        rects1 = ax.barh(y - width, data['Best of MCPybarra'], width, label='MCPybarra', color=colors['MCPybarra'])
        rects2 = ax.barh(y, data['Public Score'], width, label='Public Baseline', color=colors['Public Baseline'])
        rects3 = ax.barh(y + width, data['Best of MetaGPT'], width, label='MetaGPT', color=colors['MetaGPT'])

        ax.set_xlabel('Total Score', fontsize=24)
        ax.set_yticks(y)
        ax.set_yticklabels(simplified_names, fontsize=22)
        ax.tick_params(axis='x', labelsize=20)
        ax.invert_yaxis()  # To display top-to-bottom
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        max_score = 105 # Fixed max score for consistency
        ax.set_xlim(0, max_score)
        
        ax.bar_label(rects1, fmt='%.1f', padding=3, fontsize=16)
        ax.bar_label(rects2, fmt='%.1f', padding=3, fontsize=16)
        ax.bar_label(rects3, fmt='%.1f', padding=3, fontsize=16)
        
        return rects1, rects2, rects3

    rects1, rects2, rects3 = plot_subplot(ax1, df1)
    plot_subplot(ax2, df2)

    # Create a single legend for the entire figure, with the new desired order
    handles = [rects1[0], rects2[0], rects3[0]]
    labels = ['MCPybarra', 'Public Baseline', 'MetaGPT']
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.92), ncol=3, fontsize=24)

    fig.tight_layout(rect=[0, 0, 1, 0.9]) # Adjust layout to make space for suptitle and legend
    plt.savefig(output_path, dpi=500)
    plt.close(fig)
    print(f"Horizontal chart saved to: {output_path}")


def generate_report(df, output_path):
    """Generates a markdown report with key metrics for MCPybarra."""
    success_rate = (df['MCPybarra Improvement'] > 0).sum() / len(df) * 100
    avg_improvement = df[df['MCPybarra Improvement'] > 0]['MCPybarra Improvement'].mean()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Overall Performance Evaluation Report\n\n")
        f.write("This report compares the performance of the best server generated by the MCPybarra system and MetaGPT against the human-written public baseline for each test case.\n\n")
        f.write("## Key Metrics (MCPybarra Focus)\n\n")
        f.write(f"- **Optimization Success Rate**: **{success_rate:.2f}%**\n")
        f.write(f"  (The percentage of cases where the best MCPybarra server outperformed the public baseline.)\n\n")
        f.write(f"- **Average Magnitude of Improvement**: **+{avg_improvement:.2f} points**\n")
        f.write(f"  (The average score increase in cases where MCPybarra was successful.)\n\n")
        f.write("## Detailed Comparison Data\n\n")
        f.write(df[['Simplified Name', 'Public Score', 'Best of MCPybarra', 'Best of MetaGPT', 'MCPybarra Improvement', 'MetaGPT Improvement']].to_markdown(index=False))

    print(f"Report saved to: {output_path}")

def main():
    if not os.path.exists(RAW_SCORES_PATH):
        print(f"Error: Data source not found at {RAW_SCORES_PATH}")
        return

    print("Loading and preparing data...")
    df = load_and_prepare_data(RAW_SCORES_PATH)
    
    print("Generating comparison chart...")
    # Call the new horizontal chart function
    generate_horizontal_chart(df, CHART_OUTPUT_PATH)
    
    print("Generating analysis report...")
    generate_report(df, REPORT_OUTPUT_PATH)
    
    print("\nAnalysis complete!")

if __name__ == '__main__':
    main() 