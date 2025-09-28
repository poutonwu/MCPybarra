import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from typing import Dict, List

# --- Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw_run_data')
SUMMARY_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

# Define the directories for the 5 pipeline test runs
RUN_DIRS = [
    os.path.join(RAW_DATA_DIR, "run_20250713_034721"),
    os.path.join(RAW_DATA_DIR, "run_20250713_024028"),
    os.path.join(RAW_DATA_DIR, "run_20250713_004043"),
    os.path.join(RAW_DATA_DIR, "run_20250712_203413"),
    os.path.join(RAW_DATA_DIR, "run_20250711_204700")
]

# Define output files
OUTPUT_REPORT_MD = os.path.join(RESULTS_DIR, "pipeline_consolidated_report.md")
OUTPUT_CHART_PNG = os.path.join(RESULTS_DIR, "pipeline_consolidated_scores.png")
OUTPUT_SCORES_CSV = os.path.join(SUMMARY_DATA_DIR, "pipeline_scores_mean.csv")
OUTPUT_DURATION_CSV = os.path.join(SUMMARY_DATA_DIR, "pipeline_duration_mean.csv")
OUTPUT_TOKENS_CSV = os.path.join(SUMMARY_DATA_DIR, "pipeline_tokens_mean.csv")


def parse_md_table(md_content: str, table_header: str) -> pd.DataFrame:
    """Parses a specific markdown table from content into a pandas DataFrame."""
    try:
        pattern = re.compile(f"## {re.escape(table_header)}.*?\n\n(.*?)(?=\n\n##|\Z)", re.S)
        match = pattern.search(md_content)
        if not match:
            print(f"Warning: Table with header '{table_header}' not found.")
            return pd.DataFrame()

        table_md = match.group(1).strip()
        
        # A more robust way to handle the first column with spaces
        lines = table_md.strip().split('\n')
        header_line = lines[0]
        # Split header, keeping the first column together
        columns = [h.strip() for h in header_line.split('|')[1:-1]]
        
        data = []
        # Process data rows starting from line 2 (skipping header and separator)
        for line in lines[2:]:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) == len(columns):
                data.append(parts)
        
        df = pd.DataFrame(data, columns=columns)
        
        # The first column is the index
        df = df.set_index(columns[0])
        # The rest of the columns are data
        df = df[columns[1:]]
        
        # Convert all data to numeric, coercing errors
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop summary row if it exists
        df = df[~df.index.str.contains('Average Score|Total Duration|Total Tokens', na=False, case=False)]
        
        return df.dropna(how='all') # Drop rows where all values are NaN
    except Exception as e:
        print(f"Error parsing table '{table_header}': {e}")
        return pd.DataFrame()

def analyze_runs(run_dirs: List[str]) -> Dict[str, List[pd.DataFrame]]:
    """Analyzes all pipeline run reports and aggregates the data."""
    all_data = {
        "scores": [],
        "duration": [],
        "tokens": []
    }
    
    for run_dir in run_dirs:
        report_path = os.path.join(run_dir, "pipeline_comparison_report.md")
        if not os.path.exists(report_path):
            print(f"Warning: Report not found in {run_dir}, skipping.")
            continue
        
        print(f"Parsing report: {report_path}")
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        scores_df = parse_md_table(content, "1. Overall Score Comparison (Higher is Better)")
        duration_df = parse_md_table(content, "2. Total Duration Comparison (in seconds, Lower is Better)")
        tokens_df = parse_md_table(content, "3. Total Token Consumption (Lower is Better)")

        if not scores_df.empty:
            all_data["scores"].append(scores_df)
        if not duration_df.empty:
            all_data["duration"].append(duration_df)
        if not tokens_df.empty:
            all_data["tokens"].append(tokens_df)
            
    return all_data

def calculate_stats(data_frames: List[pd.DataFrame]) -> (pd.DataFrame, pd.DataFrame):
    """Calculates the mean and standard deviation across a list of DataFrames."""
    if not data_frames:
        return pd.DataFrame(), pd.DataFrame()
    
    # Concatenate along a new axis and calculate stats
    concat_df = pd.concat(data_frames)

    # Per user request, treat 0 as a missing value (NaN) because it indicates
    # a test that did not run properly. This affects mean and std deviation calculations.
    concat_df.replace(0, np.nan, inplace=True)
    
    mean_df = concat_df.groupby(concat_df.index).mean()
    std_df = concat_df.groupby(concat_df.index).std()
    
    return mean_df, std_df

def format_df_with_std(mean_df: pd.DataFrame, std_df: pd.DataFrame, float_format: str = ".2f") -> pd.DataFrame:
    """Formats a DataFrame to show 'mean ± std'."""
    formatted_df = pd.DataFrame(index=mean_df.index, columns=mean_df.columns)
    for row in mean_df.index:
        for col in mean_df.columns:
            mean = mean_df.loc[row, col]
            std = std_df.loc[row, col]
            if pd.notna(mean) and pd.notna(std):
                formatted_df.loc[row, col] = f"{mean:{float_format}} ± {std:{float_format}}"
            elif pd.notna(mean):
                formatted_df.loc[row, col] = f"{mean:{float_format}} ± N/A"
            else:
                formatted_df.loc[row, col] = "N/A"
    return formatted_df

def generate_report(stats: Dict[str, pd.DataFrame]):
    """Generates the final markdown report."""
    print("Generating consolidated markdown report...")
    
    with open(OUTPUT_REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("# Consolidated Pipeline Performance Report (5 Runs)\n\n")
        f.write("This report presents the aggregated results of 5 independent pipeline test runs. "
                "Values are presented as **`mean ± standard deviation`**.\n\n")
        
        # --- Overall Score ---
        f.write("## 1. Average Overall Score (Higher is Better)\n\n")
        f.write(format_df_with_std(stats['scores_mean'], stats['scores_std']).to_markdown())
        f.write("\n\n")

        # --- Duration ---
        f.write("## 2. Average Total Duration in seconds (Lower is Better)\n\n")
        if not stats['duration_mean'].empty:
            f.write(format_df_with_std(stats['duration_mean'], stats['duration_std']).to_markdown())
        else:
            f.write("Duration data was not available in the reports.\n")
        f.write("\n\n")

        # --- Token Consumption ---
        f.write("## 3. Average Total Token Consumption (Lower is Better)\n\n")
        if not stats['tokens_mean'].empty:
            f.write(format_df_with_std(stats['tokens_mean'], stats['tokens_std'], ".0f").to_markdown())
        else:
            f.write("Token consumption data was not available in the reports.\n")
        f.write("\n\n")
        
        # --- Summary Section ---
        f.write("## 4. Overall Model Performance Summary\n\n")
        avg_scores_summary = stats['scores_mean'].mean().sort_values(ascending=False)
        f.write("### Average Score Across All Servers:\n\n")
        # FIX: Changed 'header' to 'headers' for compatibility with different tabulate versions
        f.write(avg_scores_summary.to_markdown(headers=["Model", "Average Score"], floatfmt=".2f"))
        f.write("\n")
        
    print(f"Consolidated report saved to: {OUTPUT_REPORT_MD}")

def generate_chart(scores_mean: pd.DataFrame, scores_std: pd.DataFrame):
    """Generates and saves a comparison bar chart."""
    print("Generating scores comparison chart...")

    # Plotting
    fig, ax = plt.subplots(figsize=(20, 12))
    n_models = len(scores_mean.columns)
    n_servers = len(scores_mean.index)
    bar_width = 0.8 / n_models
    index = np.arange(n_servers)

    for i, model in enumerate(scores_mean.columns):
        pos = index - ((n_models - 1) / 2.0 - i) * bar_width
        ax.bar(pos, scores_mean[model], bar_width, 
               yerr=scores_std[model], capsize=5, label=model)

    ax.set_ylabel('Average Score (5 Runs)', fontsize=14)
    ax.set_title('Average Model Scores per Server (5 Runs with Std Dev)', fontsize=16)
    ax.set_xticks(index)
    ax.set_xticklabels(scores_mean.index, rotation=45, ha="right", fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_CHART_PNG, dpi=300)
    plt.close(fig)
    
    print(f"Comparison chart saved to: {OUTPUT_CHART_PNG}")

def generate_csv_reports(stats: Dict[str, pd.DataFrame]):
    """Generates CSV files for the mean statistics."""
    print("Generating CSV reports for mean statistics...")
    
    # Save scores
    stats['scores_mean'].to_csv(OUTPUT_SCORES_CSV, encoding='utf-8-sig')
    print(f"Mean scores CSV saved to: {OUTPUT_SCORES_CSV}")
    
    # Save duration
    if not stats['duration_mean'].empty:
        stats['duration_mean'].to_csv(OUTPUT_DURATION_CSV, encoding='utf-8-sig')
        print(f"Mean duration CSV saved to: {OUTPUT_DURATION_CSV}")

    # Save tokens
    if not stats['tokens_mean'].empty:
        stats['tokens_mean'].to_csv(OUTPUT_TOKENS_CSV, encoding='utf-8-sig')
        print(f"Mean tokens CSV saved to: {OUTPUT_TOKENS_CSV}")

def main():
    """Main execution function."""
    all_data = analyze_runs(RUN_DIRS)
    
    if not all_data['scores']:
        print("No score data found in any run. Aborting.")
        return

    # Calculate statistics for each metric
    scores_mean, scores_std = calculate_stats(all_data['scores'])
    duration_mean, duration_std = calculate_stats(all_data['duration'])
    tokens_mean, tokens_std = calculate_stats(all_data['tokens'])
    
    stats = {
        "scores_mean": scores_mean, "scores_std": scores_std,
        "duration_mean": duration_mean, "duration_std": duration_std,
        "tokens_mean": tokens_mean, "tokens_std": tokens_std,
    }

    # Generate the report and chart
    generate_report(stats)
    generate_chart(scores_mean, scores_std)
    generate_csv_reports(stats)

    print("\nAnalysis complete.")

if __name__ == "__main__":
    main() 