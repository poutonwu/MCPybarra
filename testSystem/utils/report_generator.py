import os
import json
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
try:
    import pandas as pd
except ImportError:
    pd = None

from testSystem.utils.utils import _simplify_public_name

def generate_pipeline_comparison_report(pipeline_results: Dict, output_dir: str, mapping_file: str, models_to_compare: List[str]):
    """Generates a pipeline comparison report for different models, including score, duration, and token consumption."""
    print("\n====== Generating Pipeline Comparison Report ======")

    if not pipeline_results:
        print("Warning: No results available to generate a pipeline comparison report.")
        return
        
    if pd is None:
        print("Warning: pandas library not installed. Cannot generate pipeline comparison report. Please run 'pip install pandas'.")
        return

    # Load mapping file to get public_server_name
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Comparison report generation failed. Pipeline mapping file not found: {mapping_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Comparison report generation failed. Invalid format in pipeline mapping file: {mapping_file}")
        return

    # 1. Parse results to build a comprehensive data list including score, duration, and tokens
    report_data = []
    
    for server_info in mapping_data:
        public_name_raw = server_info.get("public_server_name", "Unknown_Project")
        public_name = _simplify_public_name(public_name_raw)
        
        for model_name in models_to_compare:
            generated_server = server_info["generated_servers"].get(model_name)
            
            # Add a placeholder even if the model does not have a corresponding server to keep the table complete
            if not generated_server or not generated_server.get("project_name"):
                report_data.append({
                    "public_server_name": public_name,
                    "model_name": model_name,
                    "total_score": 0, "duration": 0, "tokens": 0
                })
                continue

            report_key = f"{model_name}-{generated_server['project_name']}"
            result_data = pipeline_results.get(report_key)
            
            if result_data:
                suite_summary = result_data.get("suite_summary", {})
                report_data.append({
                    "public_server_name": public_name,
                    "model_name": model_name,
                    "total_score": result_data.get("total_score", 0),
                    "duration": suite_summary.get("total_duration", 0),
                    "tokens": suite_summary.get("total_llm_tokens", 0)
                })
            else:
                # Test may have failed or not run, add a placeholder
                report_data.append({
                    "public_server_name": public_name,
                    "model_name": model_name,
                    "total_score": 0, "duration": 0, "tokens": 0
                })

    if not report_data:
        print("Error: Could not extract any valid data from test results for comparison.")
        return

    # 2. Use pandas to transform data and generate the report
    df = pd.DataFrame(report_data)
    report_path = os.path.join(output_dir, "pipeline_comparison_report.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Pipeline Model Performance Comparison Report\n\n")
        f.write("This report compares the performance of different AI models on the same server generation tasks.\n\n")

        # --- Overall Score Comparison ---
        f.write("## 1. Overall Score Comparison (Higher is Better)\n\n")
        score_pivot = df.pivot_table(index="public_server_name", columns="model_name", values="total_score", aggfunc='sum').fillna(0).astype(int)
        
        # Calculate average score ignoring zeros by replacing 0 with NaN
        average_scores = score_pivot.replace(0, np.nan).mean().round(2).fillna(0)
        score_pivot.loc['**Average Score**'] = average_scores
        
        f.write(score_pivot.to_markdown(index=True))
        f.write("\n\n")

        # --- Total Duration Comparison ---
        f.write("## 2. Total Duration Comparison (in seconds, Lower is Better)\n\n")
        duration_pivot = df.pivot_table(index="public_server_name", columns="model_name", values="duration", aggfunc='sum').fillna(0)
        duration_pivot = duration_pivot.round(2)
        duration_pivot.loc['**Total Duration**'] = duration_pivot.sum().round(2)
        f.write(duration_pivot.to_markdown(index=True))
        f.write("\n\n")

        # --- Total Token Consumption ---
        f.write("## 3. Total Token Consumption (Lower is Better)\n\n")
        token_pivot = df.pivot_table(index="public_server_name", columns="model_name", values="tokens", aggfunc='sum').fillna(0).astype(int)
        token_pivot.loc['**Total Tokens**'] = token_pivot.sum()
        f.write(token_pivot.to_markdown(index=True))

    print(f"Pipeline comparison report saved to: {report_path}")
    
    # 3. Visualize comparison chart (manually drawn with matplotlib for correct grouping)
    try:
        viz_df = score_pivot.drop('**Average Score**', errors='ignore')
        if viz_df.empty:
            print("Warning: No data available for visualization.")
            return
            
        # --- Academic Style Plotting ---
        plt.style.use('seaborn-v0_8-whitegrid') # Use a clean academic style
        
        labels = viz_df.index
        models = viz_df.columns
        x = np.arange(len(labels))  # a list of label locations
        width = 0.25  # the width of the bars
        n_models = len(models)

        fig, ax = plt.subplots(figsize=(24, 12)) # Increased figure size for readability
        
        # Define a professional color palette
        colors = plt.get_cmap('viridis')(np.linspace(0.1, 0.9, n_models))

        for i, model in enumerate(models):
            # Calculate the offset for each bar in a group
            offset = (i - (n_models - 1) / 2) * width
            rects = ax.bar(x + offset, viz_df[model], width, label=model, color=colors[i])
            # Add bar labels for clarity
            ax.bar_label(rects, padding=3, fontsize=8, fmt='%d')

        # Add some text for labels, title and axes ticks (in English)
        ax.set_ylabel('Total Score', fontsize=14)
        ax.set_title('Pipeline Model Performance Comparison (Overall Score)', fontsize=18, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10)
        ax.legend(title='Model', fontsize=12, title_fontsize=13)
        
        # Set y-axis limits to focus on the relevant score range
        ax.set_ylim(bottom=30, top=105)

        fig.tight_layout()
        
        viz_path = os.path.join(output_dir, "pipeline_comparison_scores.png")
        plt.savefig(viz_path, dpi=300) # Increase DPI for higher quality output
        print(f"Pipeline comparison chart saved to: {viz_path}")
        plt.close()
    except Exception as e:
        print(f"Error generating pipeline comparison chart: {e}")

def generate_comparison_report(public_results: Dict, refinement_results: Dict, mapping: Dict, output_dir: str):
    """Generates a comparison report."""
    print("\n====== Generating Comparison Report ======")
    
    # Prepare data
    comparison_data = []
    valid_comparisons = 0

    for public_name, refinement_name in mapping.items():
        # Flexible matching logic, supports partial matches
        public_report_name = next((k for k in public_results.keys() if public_name.lower() in k.lower()), None)
        refinement_report_name = next((k for k in refinement_results.keys() if refinement_name.lower() in k.lower()), None)
        
        if not public_report_name:
            print(f"Warning: Test results for public server '{public_name}' not found.")
            continue
            
        if not refinement_report_name:
            print(f"Warning: Test results for refined server '{refinement_name}' not found.")
            continue
        
        public_score = public_results.get(public_report_name, {}).get("total_score", 0)
        refinement_score = refinement_results.get(refinement_report_name, {}).get("total_score", 0)
        
        public_scores_dim = public_results.get(public_report_name, {}).get("scores", {})
        refinement_scores_dim = refinement_results.get(refinement_report_name, {}).get("scores", {})
        
        def format_scores(scores_dict):
            return ", ".join([f"{dim}: {score:.2f}" for dim, score in scores_dict.items()])

        comparison_data.append({
            "Public Server": public_name,
            "Public Score": f"{public_score:.2f}",
            "Refined Server": refinement_name,
            "Refined Score": f"{refinement_score:.2f}",
            "Improvement": f"{refinement_score - public_score:+.2f}",
            "Public Details": format_scores(public_scores_dim),
            "Refined Details": format_scores(refinement_scores_dim)
        })
        valid_comparisons += 1

    if not comparison_data:
        print("Error: No comparable server pairs found. Cannot generate comparison report.")
        return
        
    print(f"Successfully matched {valid_comparisons} server pairs for comparison.")

    # Generate Markdown report
    report_path = os.path.join(output_dir, "comparison_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# MCP Server Performance Comparison Report\n\n")
        
        # Write table header
        headers = comparison_data[0].keys()
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "---|"*len(headers) + "\n")
        
        # Write data rows
        for row in comparison_data:
            f.write("| " + " | ".join(map(str, row.values())) + " |\n")
    
    print(f"Comparison report saved to: {report_path}")

    # Visualize comparison
    try:
        labels = [item['Public Server'] for item in comparison_data]
        public_scores = [float(item['Public Score']) for item in comparison_data]
        refined_scores = [float(item['Refined Score']) for item in comparison_data]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(15, 8))
        rects1 = ax.bar(x - width/2, public_scores, width, label='Public')
        rects2 = ax.bar(x + width/2, refined_scores, width, label='Refined')

        ax.set_ylabel('Total Score')
        ax.set_title('Public vs. Refined Server Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.legend()
        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)
        fig.tight_layout()
        
        viz_path = os.path.join(output_dir, "comparison_scores.png")
        plt.savefig(viz_path)
        print(f"Comparison chart saved to: {viz_path}")
        plt.close(fig)
    except Exception as e:
        print(f"Error generating comparison chart: {e}")

def generate_benchmark_summary(all_benchmark_reports, output_dir):
    """Generates a summary of all benchmark test results."""
    if not all_benchmark_reports or len(all_benchmark_reports) == 0:
        print("No benchmark reports available for summary.")
        return

    print("\n====== Generating Overall Benchmark Summary Report ======")
    summary_data = []
    
    for report in all_benchmark_reports:
        # report itself is the data structure we need
        summary_data.append(report)
        
    # Save the complete summary JSON file
    summary_path = os.path.join(output_dir, "benchmark_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print(f"Benchmark summary report saved to: {summary_path}")
            
    # Extract key metrics for visualization
    report_names = []
    total_scores = []
    
    # Ensure each report has a unique name
    processed_reports = {}
    for report in summary_data:
        # report is a list, take the first element
        if report and isinstance(report, list):
            report_item = report[0]
            name = report_item.get('report_name', 'Unknown')
            # Check for duplicate report names
            if name in processed_reports:
                continue
            processed_reports[name] = report_item

    for name, report_item in processed_reports.items():
        report_names.append(name)
        total_scores.append(report_item.get('total_score', 0))

    if not report_names:
        print("No valid report data found for visualization.")
        return

    # Visualize total score comparison
    try:
        plt.figure(figsize=(15, 8))
        plt.bar(report_names, total_scores, color='skyblue')
        plt.ylabel('Total Score')
        plt.title('Benchmark Test Score Comparison')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        viz_path = os.path.join(output_dir, "benchmark_scores_summary.png")
        plt.savefig(viz_path)
        print(f"Benchmark score comparison chart saved to: {viz_path}")
        plt.close()
    except Exception as e:
        print(f"Error generating benchmark summary chart: {e}") 