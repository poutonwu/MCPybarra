import os
import re
import glob
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
import textwrap

# --- Matplotlib & Seaborn Configuration ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False 

# --- File & Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

INPUT_CSV = os.path.join(DATA_DIR, "dimensional_scores_collection.csv")
MAPPING_JSON = os.path.join(PROJECT_ROOT, 'workspace', 'pipeline_mapping.json')

# Output paths for the new composite plots
OUTPUT_DIMENSIONAL_COMPOSITE = os.path.join(RESULTS_DIR, "dimensional_analysis_composite.png")
OUTPUT_FUNCTIONALITY_COMPOSITE = os.path.join(RESULTS_DIR, "functionality_usability_composite.png")

# --- Mappings & Definitions ---
DIMENSIONS = ["Functionality", "Robustness", "Security", "Performance", "Transparency"]
SCORE_WEIGHTS = {"Functionality": 30, "Robustness": 20, "Security": 20, "Performance": 20, "Transparency": 10}
RADAR_PLOT_ORDER = ["Transparency", "Robustness", "Functionality", "Security", "Performance"] # As per user request

def get_legend_label(model_name: str) -> str:
    """Generates a standardized legend label for a model."""
    if model_name == 'Public Baseline':
        return "(Github) Public Baseline"
    elif model_name.startswith('metaGPT-'):
        display_name = model_name.replace('metaGPT-', '')
        return f"(MetaGPT) {display_name}"
    else:
        return f"(MCPybarra) {model_name}"

def get_sort_key(model_name: str) -> tuple:
    """Provides a sort key for models to ensure a consistent order."""
    if 'Public Baseline' in model_name:
        return (0, model_name)
    if 'MCPybarra' in model_name:
        return (1, model_name)
    if 'MetaGPT' in model_name:
        return (2, model_name)
    return (3, model_name)

# --- Data Loading and Preparation ---
def load_and_prepare_data(csv_path: str, mapping_path: str) -> Dict[str, pd.DataFrame]:
    """Loads all necessary data and prepares dataframes for each plot type."""
    print(f"Loading data from {csv_path}...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found: {csv_path}")

    df_wide = pd.read_csv(csv_path)
    df_long = df_wide.melt(id_vars='Test Subject', var_name='Task_Dim', value_name='Score')
    df_long = df_long[~df_long['Test Subject'].str.contains('-ave')]
    df_long.rename(columns={'Test Subject': 'Model'}, inplace=True)
    
    # --- Prepare data for Usability Plots ---
    df_func = df_long[df_long['Task_Dim'].str.contains(':Functionality')].copy()
    df_func['Task Name'] = df_func['Task_Dim'].str.replace(':Functionality', '')
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        category_mapping = json.load(f)
    name_to_category = {item['simplified_name']: item.get('category', 'Uncategorized') for item in category_mapping}
    df_func['Category'] = df_func['Task Name'].map(name_to_category).fillna('Uncategorized')

    # --- Prepare data for Radar Plot ---
    model_avg_dims = {}
    for model_name, group in df_long.groupby('Model'):
        group[['Task', 'Dimension']] = group['Task_Dim'].str.split(':', expand=True)
        # Corrected: Ignore zero scores in mean calculation for consistency
        dim_scores = group.groupby('Dimension')['Score'].apply(lambda x: x.replace(0, np.nan).mean()).fillna(0)
        model_avg_dims[model_name] = dim_scores

    # --- Prepare data for Heatmap ---
    df_long[['Task', 'Dimension']] = df_long['Task_Dim'].str.split(':', expand=True)
    df_avg = df_long.groupby(['Model', 'Task', 'Dimension'])['Score'].mean().reset_index()
    
    task_map = {item['simplified_name']: item['public_server_name'] for item in category_mapping}
    task_to_category = {item['public_server_name']: item.get('category', 'Uncategorized') for item in category_mapping}
    
    df_avg['Full_Task_Name'] = df_avg['Task'].map(task_map)
    df_avg['Category'] = df_avg['Full_Task_Name'].map(task_to_category).fillna('Uncategorized')
    
    baseline_scores = df_avg[df_avg['Model'] == 'Public Baseline'].set_index(['Task', 'Dimension'])['Score']
    df_models = df_avg[df_avg['Model'] != 'Public Baseline'].copy()
    df_models['Baseline_Score'] = df_models.set_index(['Task', 'Dimension']).index.map(baseline_scores)
    df_models['Improvement'] = df_models['Score'] - df_models['Baseline_Score']
    
    heatmap_pivot_tables = {}
    for model in df_models['Model'].unique():
        model_df = df_models[df_models['Model'] == model]
        pivot = model_df.groupby(['Category', 'Dimension'])['Improvement'].mean().unstack()
        pivot = pivot.reindex(columns=DIMENSIONS)
        heatmap_pivot_tables[model] = pivot

    print("Data preparation complete.")
    return {
        "usability_data": df_func,
        "radar_data": model_avg_dims,
        "heatmap_data": heatmap_pivot_tables
    }

# --- Composite Plot Generation Functions ---

def generate_dimensional_analysis_composite(radar_data, heatmap_data):
    """Generates the composite figure for dimensional analysis (Radar + Heatmap)."""
    print("Generating Dimensional Analysis composite plot...")
    
    # Adjust figure size for new layout, and set a white background
    fig = plt.figure(figsize=(24, 10), facecolor='white')
    
    # Create a main GridSpec: left for radar, right for heatmaps+colorbar
    gs_main = gridspec.GridSpec(1, 2, width_ratios=[1.05, 1.3], wspace=0.3, figure=fig)

    # --- (a) Radar Plot ---
    ax_radar = fig.add_subplot(gs_main[0], polar=True)
    
    labels = np.array(RADAR_PLOT_ORDER)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    
    # Sort the radar_data items based on the sort key before plotting
    sorted_radar_data = sorted(radar_data.items(), key=lambda item: get_sort_key(get_legend_label(item[0])))

    # --- New Styling for Clarity ---
    color_map = plt.get_cmap('tab10')
    style_map = {
        "(Github) Public Baseline":      {'color': color_map(0), 'marker': 'o', 'linestyle': '-', 'linewidth': 2.5},
        "(MCPybarra) gemini-2.5-pro":  {'color': color_map(2), 'marker': 's', 'linestyle': '-'},
        "(MCPybarra) gpt-4o":          {'color': color_map(3), 'marker': '^', 'linestyle': '--'},
        "(MCPybarra) qwen-max":        {'color': color_map(4), 'marker': 'D', 'linestyle': ':'},
        "(MCPybarra) qwen-plus":       {'color': color_map(1), 'marker': 'v', 'linestyle': '-.'},
        "(MCPybarra) deepseek-v3":     {'color': color_map(5), 'marker': 'p', 'linestyle': '--'},
        "(MetaGPT) qwen-plus":         {'color': color_map(6), 'marker': '*', 'linestyle': ':'},
    }

    for model_name, dims in sorted_radar_data:
        legend_label = get_legend_label(model_name)
        if not dims.empty:
            normalized_scores = [(dims.get(dim, 0) / SCORE_WEIGHTS.get(dim, 100)) * 100 for dim in RADAR_PLOT_ORDER]
            stats = np.concatenate((normalized_scores, [normalized_scores[0]]))
            angles_closed = np.concatenate((angles, [angles[0]]))
            
            style = style_map.get(legend_label, {'color': 'gray', 'marker': 'x', 'linestyle': '-'})
            
            ax_radar.plot(angles_closed, stats, 
                          label=legend_label, 
                          color=style.get('color'),
                          marker=style.get('marker'),
                          linestyle=style.get('linestyle'),
                          linewidth=style.get('linewidth', 2))
            # ax_radar.fill(angles_closed, stats, alpha=0.08) # Fill has been removed

    # --- Start of Replacement Code ---

    # Manually place labels for fine-grained control
    ax_radar.set_thetagrids(angles * 180 / np.pi, [''] * len(labels)) # Hide original labels

    # Get the y-limit to calculate label positions relative to the plot's edge
    y_max = ax_radar.get_ylim()[1] 

    for angle, label in zip(angles, labels):
        # Default distance from the edge
        radius_multiplier = 1.13  # Increase this value to move labels further out
        
        # --- THIS IS WHERE YOU ADJUST 'Transparency' ---
        if label == 'Transparency':
            # Increase the multiplier to move it UP (further away from the center)
            radius_multiplier = 1.08 # Adjusted from 1.25
        
        if label == 'Security':
            # Increase the multiplier to move it UP (further away from the center)
            radius_multiplier = 1.10 # Adjusted from 1.25
        if label == 'Functionality':
            # Increase the multiplier to move it UP (further away from the center)
            radius_multiplier = 1.11 # Adjusted from 1.25

        # ---------------------------------------------
            
        ax_radar.text(angle, y_max * radius_multiplier, label, 
                    ha='center', va='center', size=18)

    # --- End of Replacement Code ---
    ax_radar.set_theta_offset(np.pi / 2)
    ax_radar.set_theta_direction(-1)
    ax_radar.tick_params(axis='x', which='major', pad=25)
    
    # --- New: Cleaner Grid ---
    ax_radar.set_ylim(bottom=50, top=95) # Extend top limit to make more space
    ax_radar.set_rticks(np.arange(55, 95, 10)) # Reduce number of radial grid lines
    ax_radar.grid(color='grey', linestyle='--', linewidth=0.5, alpha=0.7)

    ax_radar.set_title("", y=1.1, size=16)
    # Move the legend outside the radar plot, below it
    ax_radar.legend(loc='upper center', bbox_to_anchor=(0.5, -0.04), fontsize=14, ncol=3)

    # --- (b) Heatmap Panel ---
    # Create a nested GridSpec on the right for the heatmaps and the colorbar
    gs_right = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[1], width_ratios=[22, 1], wspace=0.1)
    
    # Create the 2x2 grid for heatmaps directly from the SubplotSpec gs_right[0].
    # This resolves the TypeError and avoids creating an unnecessary intermediate Axes object.
    # hspace is reduced to compress the heatmaps vertically.
    gs_heatmap = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs_right[0], hspace=0.25, wspace=0.1)

    models_to_plot = ['gemini-2.5-pro', 'gpt-4o', 'deepseek-v3', 'qwen-max']
    
    all_values = np.concatenate([df.values.flatten() for df in heatmap_data.values() if df is not None and not df.empty])
    v_max_abs = max(abs(np.nanmin(all_values)), abs(np.nanmax(all_values)))
    norm = plt.Normalize(vmin=-v_max_abs, vmax=v_max_abs)
    cmap = 'RdYlGn'
    
    for i, model in enumerate(models_to_plot):
        ax = fig.add_subplot(gs_heatmap[i])
        df_pivot = heatmap_data.get(model)
        sns.heatmap(df_pivot, ax=ax, cmap=cmap, annot=True, fmt=".2f", linewidths=.5, cbar=False, norm=norm, annot_kws={"size": 18})
        ax.set_title(model.replace('-latest', '').upper(), fontsize=22, pad=10)
        ax.set_xlabel('')
        ax.set_ylabel('')
        if i < 2: # Hide x-axis labels for top row
            ax.tick_params(axis='x', bottom=False, labelbottom=False)
        else: # Format x-axis labels for bottom row
            ax.tick_params(axis='x', labelsize=15)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        if i % 2 != 0: # Hide y-axis labels for right column
             ax.tick_params(axis='y', left=False, labelleft=False)
        else: # Format y-axis labels for left column
             ax.tick_params(axis='y', labelsize=15)
             labels = [textwrap.fill(item.get_text().replace('/', '/\n'), width=15) for item in ax.get_yticklabels()]
             ax.set_yticklabels(labels, va='center', rotation=0)

    # Add the shared colorbar to the right of the heatmaps
    cbar_ax = fig.add_subplot(gs_right[1])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label('Average Score Improvement', size=22)

    # Use a single, comprehensive suptitle to avoid overlap
    fig.suptitle('Dimensional Analysis: (a) Overall Performance & (b) Category Improvements vs. Baseline', fontsize=30, y=0.98)
    
    # Add normalization note below radar chart
    fig.text(
        0.28, 0.11, 
        "Normalized Scores (Each dimension scaled to 100)", 
        ha='center', va='center', fontsize=15, color='gray'
    )

    # Adjust layout to make space for the suptitle and bottom text
    plt.tight_layout(rect=[0, 0.11, 1, 0.93])
    
    # Save the composite figure
    plt.savefig(OUTPUT_DIMENSIONAL_COMPOSITE, dpi=500, bbox_inches='tight')
    plt.close()
    print(f"Dimensional analysis composite plot saved to: {OUTPUT_DIMENSIONAL_COMPOSITE}")


def generate_functionality_usability_composite(usability_data):
    """Generates the 1x3 composite figure for functionality usability."""
    print("Generating Functionality Usability composite plot...")
    
    # Changed figsize for horizontal layout and gs for 1x3 grid
    fig = plt.figure(figsize=(28, 10))
    # Adjusted wspace for better label fitting
    gs = gridspec.GridSpec(1, 3, hspace=0.25, wspace=0.05)
    
    # Common plotting properties
    category_order = ["Perfectly Usable (27-30)", "Highly Usable (24-26)", "Partially Usable (18-23)", "Almost Unusable (<18)"]
    colors = ['#2ca02c', '#98df8a', '#ffc107', '#d62728'] # Dark Green, Light Green, Amber, Red
    
    # --- Overall Usability Plot (a) has been removed as per request ---

    # --- (a, b, c) Category Breakdown Plots ---
    categories = sorted([cat for cat in usability_data['Category'].unique() if cat != 'Uncategorized'])
    
    # Remapped subplots to a 1x3 grid
    subplot_map = {categories[0]: gs[0, 0], categories[1]: gs[0, 1], categories[2]: gs[0, 2]}
    # Updated titles to a, b, c
    subplot_titles = {'Application/System Integration': '(a)', 'Data/Content Retrieval': '(b)', 'File/Format Processing': '(c)'}
    # Categories for which to hide the y-axis labels (all but the first)
    hide_y_label_categories = categories[1:]

    # Get model order once for consistency across all subplots
    models = sorted(usability_data['Model'].unique())
    model_order = sorted(models, key=lambda x: get_sort_key(get_legend_label(x)), reverse=True)

    last_ax = None
    for i, category in enumerate(categories):
        spec = subplot_map[category]
        ax = fig.add_subplot(spec)
        last_ax = ax # Save the last axis for the legend
        category_df = usability_data[usability_data['Category'] == category]
        
        cat_plot_data = {}
        cat_total_tasks = category_df['Task Name'].nunique()
        for model in models:
            model_df = category_df[category_df['Model'] == model]
            # Corrected: Ignore zero scores in mean calculation for consistency
            avg_scores = model_df.groupby('Task Name')['Score'].apply(lambda x: x.replace(0, np.nan).mean()).fillna(0)
            counts = {
                category_order[0]: avg_scores[avg_scores >= 27].count(),
                category_order[1]: avg_scores[(avg_scores >= 24) & (avg_scores < 27)].count(),
                category_order[2]: avg_scores[(avg_scores >= 18) & (avg_scores < 24)].count(),
                category_order[3]: avg_scores[avg_scores < 18].count()
            }
            cat_plot_data[model] = {k: (v / cat_total_tasks * 100) if cat_total_tasks > 0 else 0 for k, v in counts.items()}
        
        cat_plot_df = pd.DataFrame(cat_plot_data).T[category_order]
        cat_plot_df = cat_plot_df.loc[model_order] # Use same model order
        cat_plot_df.index = [get_legend_label(name) for name in cat_plot_df.index]
        
        cat_plot_df.plot(kind='barh', stacked=True, color=colors, ax=ax, width=0.8, legend=False)
        title_prefix = subplot_titles.get(category, '')
        ax.set_title(f'{title_prefix} Usability for: {category} (n={cat_total_tasks})', fontsize=24, pad=15, y=0.97)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Distribution of Tasks in Category (%)', fontsize=24)
        ax.tick_params(axis='x', labelsize=22)
        ax.grid(False) # Remove grid lines
        # Remove all spines except the bottom one
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Hide y-axis labels for the 2nd and 3rd plots
        if category in hide_y_label_categories:
            ax.tick_params(axis='y', left=False, labelleft=False)
        else:
            ax.tick_params(axis='y', labelsize=24, length=0)

        for c in ax.containers:
            # Hide labels for zero values
            ax.bar_label(c, fmt=lambda v: f'{v:.1f}%' if v > 0.1 else '', label_type='center', color='white', weight='bold', fontsize=21)
            
    fig.suptitle('Comprehensive Analysis of Functionality Usability', fontsize=32, y=0.99)
    
    if last_ax:
        handles, labels = last_ax.get_legend_handles_labels()
        # Adjusted bbox_to_anchor for horizontal layout by increasing the y-value
        fig.legend(handles, labels, title='Usability Tier', bbox_to_anchor=(0.5, -0.1), loc='lower center', ncol=4, fontsize=24, title_fontsize=26)
    
    # Adjusted rect for new layout
    plt.tight_layout(rect=[0, 0.1, 1, 0.90])

    plt.savefig(OUTPUT_FUNCTIONALITY_COMPOSITE, dpi=500, bbox_inches='tight')
    plt.close()
    print(f"Functionality usability composite plot saved to: {OUTPUT_FUNCTIONALITY_COMPOSITE}")


if __name__ == "__main__":
    prepared_data = load_and_prepare_data(INPUT_CSV, MAPPING_JSON)
    
    generate_dimensional_analysis_composite(
        radar_data=prepared_data["radar_data"],
        heatmap_data=prepared_data["heatmap_data"]
    )
    
    generate_functionality_usability_composite(
        usability_data=prepared_data["usability_data"]
    )

    print("\nComposite plot generation script finished.") 