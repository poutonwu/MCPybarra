import os
import json
import re
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List
from langchain_core.messages import HumanMessage
from testSystem.prompts.utils import load_prompt




class Reporter:
    """Handles report generation, scoring, and visualization of test results."""
    
    def __init__(self, output_dir: str, llm=None, agent_logger=None, file_reader_tool=None):
        """Initializes the reporter.
        
        Args:
            output_dir: The directory for report output.
            llm: The LLM instance for generating detailed reports.
            agent_logger: The agent logger for logging events.
            file_reader_tool: The tool for reading test files.
        """
        self.output_dir = output_dir
        self.llm = llm
        self.agent_logger = agent_logger
        self.file_reader_tool = file_reader_tool
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_test_files(self) -> List[str]:
        """Gets the list of files in the test area."""
        if not self.file_reader_tool:
            return []
        try:
            # Use the file reader tool to list all files
            result = self.file_reader_tool._run(list_files=True)
            print(f"Found {len(result)} files in the test area.")
            return result
        except Exception as e:
            print(f"Error getting test file list: {str(e)}")
            return []

    async def generate_detailed_report(self, results: Dict) -> str:
        """Generates a more detailed test report using an LLM and scores it.
        
        Args:
            results: The test results.
            
        Returns:
            A detailed test report in Markdown format.
        """
        if not self.llm:
            print("Warning: LLM is not available, cannot generate a detailed report.")
            return None
            
        try:
            test_files = self.get_test_files()
            
            prompt_template = load_prompt("reporting/detailed_report.prompt")
            prompt = prompt_template.format(
                results_json=json.dumps(results, ensure_ascii=False, indent=2),
                functional_weight=SCORE_WEIGHTS['功能性'],
                robustness_weight=SCORE_WEIGHTS['健壮性'],
                security_weight=SCORE_WEIGHTS['安全性'],
                performance_weight=SCORE_WEIGHTS['性能'],
                transparency_weight=SCORE_WEIGHTS['透明性']
            )
            
            report_start_time = time.time()
            report_name = results.get("report_name", results["server_name"])
            response = self.llm.invoke([HumanMessage(content=prompt)])
            report_end_time = time.time()
            if self.agent_logger:
                self.agent_logger.log(event_type="llm_test_report_generated", 
                                      report_name=report_name,
                                      report_generate_time=report_end_time - report_start_time,
                                      test_report=response.content[:800]
                                      )
            
            report_content = f"# {results['server_name']} Test Report\n\n"
            report_content += f"Server Directory: {results.get('parent_dir', '')}\n"
            report_content += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            report_content += response.content
            
            self._extract_and_save_scores(results, response.content)
            
            report_file = os.path.join(self.output_dir, f"detailed_report_{report_name}.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            print(f"Detailed test report saved to: {report_file}")
            return report_content
            
        except Exception as e:
            print(f"Error generating detailed report: {e}")
            results["scores"] = {"功能性": 0, "性能": 0 ,"健壮性": 0, "安全性": 0, "透明性": 0}
            results["total_score"] = 0
            return None

    def _extract_and_save_scores(self, results: Dict, report_content: str):
        """Extracts scores from the report content and saves them to the results dictionary."""
        try:
            scores_pattern = r'<SCORES>(.*?)</SCORES>'
            scores_match = re.search(scores_pattern, report_content, re.DOTALL)
            
            dimension_scores = {dim: 0 for dim in SCORE_DIMENSIONS}
            total_score = 0
            
            if scores_match:
                scores_text = scores_match.group(1).strip()
                for line in scores_text.split('\n'):
                    # Keep Chinese keys for parsing
                    for dimension, weight in SCORE_WEIGHTS.items():
                        if line.startswith(dimension) or line.startswith(DIMENSION_MAP_EN[dimension]):
                            match = re.search(r'(\d+)/' + str(weight), line)
                            if match:
                                dimension_scores[dimension] = int(match.group(1))
                    if line.startswith("总分") or line.startswith("Total Score"):
                        match = re.search(r'(\d+)/100', line)
                        if match:
                            total_score = int(match.group(1))
            
            if total_score == 0:
                total_score = sum(dimension_scores.values())
            
            results["scores"] = dimension_scores
            results["total_score"] = total_score
            print(f"Extracted scores: {dimension_scores}, Total score: {total_score}")
            
        except Exception as e:
            print(f"Failed to extract scores from report: {e}")
            results["scores"] = {dim: 0 for dim in SCORE_DIMENSIONS}
            results["total_score"] = 0

    def visualize_results(self, report_name: str, results: Dict) -> None:
        """Visualizes the test results for a single server."""
        if not results.get("test_results"):
            print(f"No test results available for visualization for {report_name}")
            return
            
        viz_dir = os.path.join(self.output_dir, "visualizations")
        os.makedirs(viz_dir, exist_ok=True)
        
        self._plot_response_times(report_name, results, viz_dir)
        self._plot_test_case_counts(report_name, results, viz_dir)
        self._plot_combined_score_chart(report_name, results, viz_dir)
        
        print(f"Visualization results saved to: {viz_dir}")

    def _plot_response_times(self, report_name, results, viz_dir):
        tool_names, avg_times = [], []
        for tool_name, tool_results in results["test_results"].items():
            if tool_results:
                tool_names.append(tool_name)
                avg_times.append(sum(r["execution_time"] for r in tool_results) / len(tool_results))
        
        if tool_names:
            plt.figure(figsize=(10, 6))
            plt.bar(tool_names, avg_times)
            plt.title(f'{report_name} - Average Tool Response Time')
            plt.xlabel('Tool Name')
            plt.ylabel('Average Response Time (s)')
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, f'{report_name}_tool_response_times.png'))
            plt.close()

    def _plot_test_case_counts(self, report_name, results, viz_dir):
        tool_names, case_counts = [], []
        for tool_name, tool_results in results["test_results"].items():
            tool_names.append(tool_name)
            case_counts.append(len(tool_results))

        if tool_names:
            plt.figure(figsize=(10, 6))
            plt.bar(tool_names, case_counts)
            plt.title(f'{report_name} - Number of Test Cases per Tool')
            plt.xlabel('Tool Name')
            plt.ylabel('Number of Test Cases')
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, f'{report_name}_test_case_counts.png'))
            plt.close()
            
    def _plot_combined_score_chart(self, report_name, results, viz_dir):
        """Plots the normalized radar chart and the raw score bar chart on the same canvas."""
        if "scores" not in results:
            return

        scores = results["scores"]
        
        # 1. Create a canvas with two subplots
        fig = plt.figure(figsize=(20, 8))
        fig.suptitle(f'{report_name} - Comprehensive Performance Evaluation', fontsize=20)
        
        # --- 2. Left subplot: Normalized Radar Chart ---
        ax1 = fig.add_subplot(1, 2, 1, polar=True)
        
        normalized_scores = [
            (scores.get(dim, 0) / SCORE_WEIGHTS[dim]) * 20 if SCORE_WEIGHTS[dim] > 0 else 0
            for dim in SCORE_DIMENSIONS
        ]
        
        # Use English labels for the chart
        labels_en = [DIMENSION_MAP_EN[dim] for dim in SCORE_DIMENSIONS]
        N = len(labels_en)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1] # Close the plot

        line_color = '#4285F4' # Google Blue
        
        ax1.plot(angles, normalized_scores + [normalized_scores[0]], linewidth=2, linestyle='solid', color=line_color)
        ax1.fill(angles, normalized_scores + [normalized_scores[0]], color=line_color, alpha=0.2)

        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(labels_en, size=14)
        ax1.set_rlabel_position(0)
        
        ax1.set_yticks([5, 10, 15, 20])
        ax1.set_yticklabels(["5", "10", "15", "20"], color="grey", size=10)
        ax1.set_ylim(0, 20)
        
        ax1.set_title('Normalized Performance Score Radar Chart', size=16, y=1.12)

        # --- 3. Right subplot: Raw Score Bar Chart ---
        ax2 = fig.add_subplot(1, 2, 2)
        
        max_scores = [SCORE_WEIGHTS[d] for d in SCORE_DIMENSIONS]
        actual_scores = [scores.get(d, 0) for d in SCORE_DIMENSIONS]
        
        index = np.arange(len(labels_en))
        
        # Plot background bars (max score)
        ax2.bar(labels_en, max_scores, color='#E0E0E0', label='Max Score')
        # Plot foreground bars (actual score)
        bars = ax2.bar(labels_en, actual_scores, color=line_color, label='Actual Score')
        
        # Add "score/max" text labels on the bars
        for i, bar in enumerate(bars):
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.3, f'{actual_scores[i]}/{max_scores[i]}', va='bottom', ha='center', fontsize=12)

        ax2.set_ylabel('Score', fontsize=14)
        ax2.set_xticks(index)
        ax2.set_xticklabels(labels_en, fontsize=14, rotation=30, ha="right")
        ax2.set_title('Raw Scores per Dimension', size=16)
        ax2.legend()
        ax2.set_ylim(0, max(max_scores) * 1.15) # Leave space at the top

        # --- 4. Adjust layout and save the entire canvas ---
        plt.tight_layout(rect=[0, 0, 1, 0.95]) # Leave space for the main title
        plt.savefig(os.path.join(viz_dir, f'{report_name}_radar_chart.png'))
        plt.close()

    def save_test_report(self, results: Dict) -> None:
        """Saves the JSON-formatted test report to a file."""
        report_name = results.get("report_name", results["server_name"])
        report_file = os.path.join(self.output_dir, f"test_report_{report_name}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"JSON test report saved to: {report_file}") 

# Remove Chinese font support
plt.rcParams['axes.unicode_minus'] = False

# Score weights - keys must remain in Chinese for report parsing
SCORE_WEIGHTS = {
    "功能性": 30,
    "健壮性": 20,
    "安全性": 20,
    "性能": 20,
    "透明性": 10,
}
SCORE_DIMENSIONS = list(SCORE_WEIGHTS.keys())

# English mapping for chart labels
DIMENSION_MAP_EN = {
    "功能性": "Functionality",
    "健壮性": "Robustness",
    "安全性": "Security",
    "性能": "Performance",
    "透明性": "Transparency",
}