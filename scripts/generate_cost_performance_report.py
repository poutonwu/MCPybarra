import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'summary_data')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

RAW_SCORES_CSV = os.path.join(DATA_DIR, "raw_scores_collection.csv")
AVERAGE_COSTS_CSV = os.path.join(DATA_DIR, "average_costs.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "cost_performance_summary.csv")
OUTPUT_CHART = os.path.join(RESULTS_DIR, "performance_cost_analysis.png")

def load_data():
    """加载分数和成本数据"""
    print("正在加载分数和成本数据...")
    if not os.path.exists(RAW_SCORES_CSV) or not os.path.exists(AVERAGE_COSTS_CSV):
        print(f"错误: 缺少一个或多个输入文件。请确保以下文件存在:")
        print(f"  - {RAW_SCORES_CSV}")
        print(f"  - {AVERAGE_COSTS_CSV}")
        return None, None
        
    df_scores = pd.read_csv(RAW_SCORES_CSV)
    df_costs = pd.read_csv(AVERAGE_COSTS_CSV)
    print("数据加载完成。")
    return df_scores, df_costs

def process_data(df_scores, df_costs):
    """处理和整合数据，计算性价比"""
    print("正在处理和整合数据...")
    # 1. 提取模型的平均分
    df_avg_scores = df_scores[df_scores['Test Subject'].str.contains('-ave')].copy()
    df_avg_scores['Model'] = df_avg_scores['Test Subject'].str.replace('-ave', '')
    avg_scores = df_avg_scores[['Model', 'Average score']].set_index('Model')

    # 2. 计算每个模型的平均成本
    avg_costs = df_costs.groupby('Model')['Total Cost (USD)'].mean().reset_index()
    avg_costs = avg_costs.rename(columns={'Total Cost (USD)': 'Average Cost (USD)'}).set_index('Model')

    # 3. 合并平均分和平均成本
    df_summary = pd.merge(avg_scores, avg_costs, on='Model', how='inner')
    
    # 4. 计算性价比 (每美元得分)
    # 为避免除以零，将0成本替换为一个极小值
    df_summary['Score per Dollar'] = df_summary['Average score'] / df_summary['Average Cost (USD)'].replace(0, 1e-9)
    
    # 5. 提取每个任务的平均分
    score_cols = [col for col in df_avg_scores.columns if col not in ['Test Subject', 'Model', 'Average score', 'Standard deviation', 'Testable Tasks', 'Testability Rate']]
    task_scores = df_avg_scores[['Model'] + score_cols]
    
    # 清理任务分数，只保留数字
    for col in score_cols:
        task_scores[col] = task_scores[col].astype(str).str.extract(r'([\d\.]+)').astype(float)
        
    task_scores = task_scores.set_index('Model')

    # 6. 将任务分数合并到总表中
    df_final = pd.merge(df_summary, task_scores, on='Model', how='left')

    print("数据处理完成。")
    return df_final.sort_values(by='Score per Dollar', ascending=False)


def generate_chart(df_summary):
    """生成成本-性能散点图"""
    print("正在生成成本-性能散点图...")
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))

    # 绘制散点图
    sns.scatterplot(
        data=df_summary,
        x='Average Cost (USD)',
        y='Average score',
        hue='Model',
        size='Score per Dollar',
        sizes=(100, 1000),
        alpha=0.8,
        palette='viridis',
        ax=ax
    )

    # 为每个点添加标签
    for i, row in df_summary.iterrows():
        ax.text(row['Average Cost (USD)'] * 1.02, row['Average score'], row.name, fontsize=10)

    # 设置图表标题和标签
    ax.set_title('Cost vs. Performance Analysis of AI Models', fontsize=18, weight='bold')
    ax.set_xlabel('Average Cost per Project (USD)', fontsize=12)
    ax.set_ylabel('Average Score', fontsize=12)
    
    # 优化图例
    handles, labels = ax.get_legend_handles_labels()
    # 分离颜色和大小图例
    color_legend_handles = handles[1:len(df_summary)+1]
    color_legend_labels = labels[1:len(df_summary)+1]
    size_legend_handles = handles[len(df_summary)+2:]
    size_legend_labels = [f"{float(l):.1f}" for l in labels[len(df_summary)+2:]] # 格式化大小标签

    ax.legend(color_legend_handles, color_legend_labels, title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')

    # 创建第二个图例用于大小
    size_legend = fig.add_axes([0.93, 0.15, 0.1, 0.25]) # x, y, width, height
    size_legend.set_title('Score per $', pad=10)
    for i, handle in enumerate(size_legend_handles):
        size_legend.scatter([], [], s=handle.get_sizes()[0], label=size_legend_labels[i], color='gray', alpha=0.7)
    size_legend.legend(loc='center', frameon=False, handletextpad=-0.5)
    size_legend.axis('off')

    plt.tight_layout(rect=[0, 0, 0.85, 1]) # 调整布局为图例留出空间
    plt.savefig(OUTPUT_CHART, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图表已保存到: {OUTPUT_CHART}")


def main():
    """主函数，执行整个分析流程"""
    df_scores, df_costs = load_data()
    if df_scores is None:
        return
        
    df_summary = process_data(df_scores, df_costs)
    
    # 保存CSV报告
    df_summary.to_csv(OUTPUT_CSV, encoding='utf-8-sig')
    print(f"成本-性能摘要报告已保存到: {OUTPUT_CSV}")
    
    # 生成图表
    generate_chart(df_summary)
    
    print("\n所有任务完成!")


if __name__ == "__main__":
    main() 