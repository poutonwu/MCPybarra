import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

# 使用'Agg'后端，避免在无图形界面的环境中出错
matplotlib.use('Agg')

# --- Path Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

DIMENSIONAL_DATA_CSV = os.path.join(DATA_DIR, 'dimensional_scores_collection.csv')
OUTPUT_COMBINED_HEATMAP = os.path.join(RESULTS_DIR, 'dimensional_improvement_by_category_combined.png')

# 维度定义 (按期望的显示顺序)
DIMENSIONS = ["Functionality", "Robustness", "Security", "Performance", "Transparency"]

# 服务器类别定义
SERVER_CATEGORIES = {
    "Data/Content Retrieval": [
        "unsplash-mcp-server-main", "mcp-server-data-exploration-main", "mcp-everything-search-main",
        "flights-mcp-main", "huggingface-mcp-server-main", "duckduckgo-mcp-server-main",
        "arxiv-mcp-server-main", "academic-search-mcp-server-master", "tavily-mcp-server-main",
        "financial-data-mcp-server-main", "git-mcp-server", "ssh-mcp-server-main", "image-search-mcp-server"
    ],
    "File/Format Processing": [
        "image-converter-mcp-server-main", "word-processor-office-mcp-server-main", "zotero-mcp-server-main",
        "word-automation-doc-mcp-server-main", "pdf-tools-mcp-server-main", "text-editor-mcp-server-main",
        "markdown-mcp-server-main"
    ],
    "Application/System Integration": [
        "mongodb-mcp-server-main", "mysql-mcp-server-main", "outlook-mcp-server-main",
        "opencv-mcp-server-main", "screenshot-mcp-server-main"
    ]
}

# 将CSV中的任务名映射到完整的任务标识符
TASK_NAME_MAP = {
    'Academic Search': 'academic-search-mcp-server-master', 'Arxiv': 'arxiv-mcp-server-main',
    'Data Exploration': 'mcp-server-data-exploration-main', 'Duckduckgo': 'duckduckgo-mcp-server-main',
    'Everything Search': 'mcp-everything-search-main', 'Financial Data': 'financial-data-mcp-server-main',
    'Flights': 'flights-mcp-main', 'Git': 'git-mcp-server', 'Huggingface': 'huggingface-mcp-server-main',
    'Image Converter': 'image-converter-mcp-server-main', 'Image Search': 'image-search-mcp-server',
    'Markdown': 'markdown-mcp-server-main', 'Mongodb': 'mongodb-mcp-server-main', 'Mysql': 'mysql-mcp-server-main',
    'Opencv': 'opencv-mcp-server-main', 'Outlook': 'outlook-mcp-server-main', 'Pdf Tools': 'pdf-tools-mcp-server-main',
    'Screenshot': 'screenshot-mcp-server-main', 'Ssh': 'ssh-mcp-server-main', 'Tavily': 'tavily-mcp-server-main',
    'Text Editor': 'text-editor-mcp-server-main', 'Unsplash': 'unsplash-mcp-server-main',
    'Word Automation (Doc)': 'word-automation-doc-mcp-server-main',
    'Word Processor (Office)': 'word-processor-office-mcp-server-main', 'Zotero': 'zotero-mcp-server-main'
}


def load_and_prepare_data(csv_path):
    """加载、转换并准备用于分析的数据。"""
    print(f"正在从 {csv_path} 加载数据...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"数据文件未找到: {csv_path}")

    df_wide = pd.read_csv(csv_path)
    
    df_long = df_wide.melt(id_vars='Test Subject', var_name='Task_Dim', value_name='Score')
    df_long = df_long[~df_long['Test Subject'].str.contains('-ave')]
    
    df_long[['Task', 'Dimension']] = df_long['Task_Dim'].str.split(':', expand=True)
    df_long.rename(columns={'Test Subject': 'Model'}, inplace=True)
    
    # 关键步骤：按模型、任务和维度对分数进行平均
    df_avg = df_long.groupby(['Model', 'Task', 'Dimension'])['Score'].mean().reset_index()

    # 映射任务名称并添加类别
    df_avg['Full_Task_Name'] = df_avg['Task'].map(TASK_NAME_MAP)
    
    task_to_category = {task: category for category, tasks in SERVER_CATEGORIES.items() for task in tasks}
    df_avg['Category'] = df_avg['Full_Task_Name'].map(task_to_category).fillna('Uncategorized')
    
    print("数据准备完成。")
    return df_avg

def calculate_improvement_scores(df_avg):
    """根据基线计算改进分数并创建数据透视表。"""
    print("正在计算改进分数...")
    baseline_scores = df_avg[df_avg['Model'] == 'Public Baseline'].set_index(['Task', 'Dimension'])['Score']
    
    df_models = df_avg[df_avg['Model'] != 'Public Baseline'].copy()
    
    df_models['Baseline_Score'] = df_models.set_index(['Task', 'Dimension']).index.map(baseline_scores)
    df_models['Improvement'] = df_models['Score'] - df_models['Baseline_Score']
    
    pivot_tables = {}
    for model in df_models['Model'].unique():
        if model == 'Public Baseline': continue
        model_df = df_models[df_models['Model'] == model]
        pivot = model_df.groupby(['Category', 'Dimension'])['Improvement'].mean().unstack()
        pivot = pivot.reindex(columns=DIMENSIONS) # 确保列顺序正确
        pivot_tables[model] = pivot
        
    return pivot_tables

def generate_combined_heatmap(df_pivot_dict, models):
    """生成一个极简、具有学术审美风格的2x2组合热力图。"""
    print("正在生成组合热力图...")
    # 共享轴，并稍微调整图形尺寸
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
    axes = axes.flatten()

    all_values = np.concatenate([df.values.flatten() for df in df_pivot_dict.values() if df is not None])
    v_max_abs = max(abs(np.nanmin(all_values)), abs(np.nanmax(all_values)))
    norm = plt.Normalize(vmin=-v_max_abs, vmax=v_max_abs)
    cmap = 'RdYlGn'

    for i, model in enumerate(models):
        if i >= len(axes): break
        
        ax = axes[i]
        df_pivot = df_pivot_dict.get(model)
        
        display_name = model.replace('-latest', '').upper()
        ax.set_title(display_name, fontsize=16, pad=15)
        
        if df_pivot is None or df_pivot.empty:
            ax.text(0.5, 0.5, f'No data for\n{model}', ha='center', va='center', fontsize=12, color='grey')
            ax.spines[:].set_visible(False)
            ax.tick_params(axis='both', which='both', length=0)
            continue

        sns.heatmap(df_pivot, ax=ax, cmap=cmap, annot=True, fmt=".2f", linewidths=.5, cbar=False, norm=norm, annot_kws={"size": 11})
        ax.tick_params(axis='y', labelrotation=0)
        
        # 清除由seaborn自动添加的多余轴标签
        ax.set_xlabel('')
        ax.set_ylabel('')

    # 旋转底部图表的刻度标签
    for ax in [axes[2], axes[3]]:
         plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # 调整布局以适应没有主标题和轴标签的情况
    # 增加左边距(left)以防止标签被截断，并相应调整右边距(right)
    fig.subplots_adjust(left=0.2, right=0.85, top=0.92, bottom=0.15, hspace=0.3, wspace=0.05)

    # 添加共享颜色条
    # 相应地调整颜色条的位置
    cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.77])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label('Average Score Improvement', size=14)

    plt.savefig(OUTPUT_COMBINED_HEATMAP, dpi=300)
    plt.close()
    print(f"组合热力图已保存到: {OUTPUT_COMBINED_HEATMAP}")


if __name__ == "__main__":
    df_avg_processed = load_and_prepare_data(DIMENSIONAL_DATA_CSV)
    pivot_tables = calculate_improvement_scores(df_avg_processed)
    
    models_to_plot = ['gemini-2.5-pro', 'gpt-4o', 'deepseek-v3', 'qwen-max']
    generate_combined_heatmap(pivot_tables, models_to_plot)
    
    print("\n所有任务完成!") 