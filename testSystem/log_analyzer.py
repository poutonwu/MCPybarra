import json
import os
import glob
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Tuple, Optional
import re

plt.rcParams['axes.unicode_minus'] = False

class LogAnalyzer:
    """A utility class for analyzing multi-agent system logs, with a focus on academic evaluation metrics."""
    
    def __init__(self, log_dir: str = "../logs/agent_logs/"):
        """Initializes the log analyzer.
        
        Args:
            log_dir: Path to the log file directory.
        """
        self.log_dir = log_dir
        self.agents_data = {}
        self.all_events = set()
        
    def load_logs(self, log_files: Optional[List[str]] = None, pattern: str = "*.jsonl") -> Dict[str, List[Dict]]:
        """Loads log files.
        
        Args:
            log_files: (Optional) A list of log file names. Will be combined with self.log_dir.
            pattern: If log_files is not provided, this pattern is used to find files in log_dir.

        Returns:
            A dictionary of log entries grouped by agent.
        """
        if log_files:
            # Combine file names in log_files with log_dir to form full paths
            files_to_load = [os.path.join(self.log_dir, f) for f in log_files]
        else:
            files_to_load = glob.glob(os.path.join(self.log_dir, pattern))
        
        agents_data = {}
        
        for file_path in files_to_load:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    entries = [json.loads(line) for line in f if line.strip()]
                
                if entries:
                    agent_name = entries[0].get('agent', 'unknown')
                    timestamp = entries[0].get('timestamp', '')
                    
                    # Add this batch of data to the corresponding agent's list
                    if agent_name not in agents_data:
                        agents_data[agent_name] = []
                    
                    agents_data[agent_name].extend(entries)
                    
                    # Collect all event types
                    for entry in entries:
                        if 'event' in entry:
                            self.all_events.add(entry['event'])
                            
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
        
        self.agents_data = agents_data
        return agents_data
        
    def calculate_duration(self, 
                          agent_name: str, 
                          start_event: str = 'start_node', 
                          end_event: str = 'end_node') -> Dict[str, float]:
        """Calculates the duration of specific agent tasks.
        
        Args:
            agent_name: Agent name.
            start_event: Start event type.
            end_event: End event type.
            
        Returns:
            Duration of each task batch in seconds.
        """
        if agent_name not in self.agents_data:
            return {}
            
        entries = self.agents_data[agent_name]
        
        # Sort by timestamp
        entries = sorted(entries, key=lambda x: x.get('timestamp', ''))
        
        durations = {}
        batch_start = None
        batch_id = 0
        
        for entry in entries:
            event = entry.get('event')
            timestamp = entry.get('timestamp')
            
            if not event or not timestamp:
                continue
                
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                if event == start_event:
                    batch_start = dt
                    batch_id += 1
                elif event == end_event and batch_start:
                    duration = (dt - batch_start).total_seconds()
                    durations[f"batch_{batch_id}"] = duration
                    batch_start = None
            except Exception as e:
                print(f"Error processing timestamp {timestamp}: {str(e)}")
                
        return durations
    
    def compute_tool_efficiency(self) -> Dict[str, Dict[str, float]]:
        """Calculates tool call efficiency (success rate and average response time).
        
        Returns:
            Tool call efficiency for each agent.
        """
        efficiency_stats = {}
        
        for agent, entries in self.agents_data.items():
            if agent not in efficiency_stats:
                efficiency_stats[agent] = {
                    'tool_call_count': 0,
                    'tool_success_count': 0,
                    'total_response_time': 0,
                    'success_rate': 0.0,
                    'avg_response_time': 0.0
                }
                
            tool_calls = {}  # Temporarily store tool calls, key is call ID
            
            for entry in entries:
                if entry.get('event') == 'tool_call':
                    call_id = entry.get('call_id', str(hash(str(entry))))
                    tool_calls[call_id] = {
                        'tool': entry.get('tool'),
                        'start_time': datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00')),
                        'success': False
                    }
                    efficiency_stats[agent]['tool_call_count'] += 1
                    
                elif entry.get('event') == 'tool_result':
                    call_id = entry.get('call_id')
                    if call_id in tool_calls:
                        end_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                        tool_call = tool_calls[call_id]
                        response_time = (end_time - tool_call['start_time']).total_seconds()
                        
                        # Check if the result was successful (simple check for 'error' keyword)
                        result = entry.get('result', '')
                        is_success = 'error' not in str(result).lower()
                        
                        if is_success:
                            efficiency_stats[agent]['tool_success_count'] += 1
                            efficiency_stats[agent]['total_response_time'] += response_time
            
            # Calculate success rate and average response time
            if efficiency_stats[agent]['tool_call_count'] > 0:
                efficiency_stats[agent]['success_rate'] = efficiency_stats[agent]['tool_success_count'] / efficiency_stats[agent]['tool_call_count']
                
            if efficiency_stats[agent]['tool_success_count'] > 0:
                efficiency_stats[agent]['avg_response_time'] = efficiency_stats[agent]['total_response_time'] / efficiency_stats[agent]['tool_success_count']
                
        return efficiency_stats
    
    def compute_llm_usage(self) -> Dict[str, Dict[str, Any]]:
        """Calculates LLM usage for each agent.
        
        Returns:
            LLM usage statistics for each agent.
        """
        usage_stats = {}
        llm_calls = {}  # Track LLM calls
        
        for agent, entries in self.agents_data.items():
            usage_stats[agent] = {
                'n_calls': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'total_latency': 0.0,
                'avg_latency': 0.0,
                'tokens_per_call': 0.0
            }
            
            for entry in entries:
                if entry.get('event') == 'llm_invoke':
                    usage_stats[agent]['n_calls'] += 1
                    call_id = entry.get('call_id')
                    if call_id:
                        llm_calls[call_id] = {
                            'start_time': datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                        }
                    
                    # Extract prompt token count
                    if 'usage_metadata' in entry:
                        metadata = entry['usage_metadata']
                        prompt_tokens = metadata.get('input_tokens', 0)
                        if prompt_tokens > 0:
                            usage_stats[agent]['prompt_tokens'] += prompt_tokens
                            # Update total tokens at the same time
                            usage_stats[agent]['total_tokens'] += prompt_tokens
                    
                elif entry.get('event') == 'llm_response':
                    call_id = entry.get('call_id')
                    if call_id in llm_calls:
                        end_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                        llm_call = llm_calls[call_id]
                        latency = (end_time - llm_call['start_time']).total_seconds()
                        usage_stats[agent]['total_latency'] += latency
                        
                        if 'usage_metadata' in entry:
                            metadata = entry['usage_metadata']
                            output_tokens = metadata.get('output_tokens', 0)
                            usage_stats[agent]['completion_tokens'] += output_tokens
                            usage_stats[agent]['total_tokens'] += output_tokens
                
                # Also handle llm_token_usage events to ensure no token statistics are missed
                elif entry.get('event') == 'llm_token_usage' and 'usage_metadata' in entry:
                    metadata = entry['usage_metadata']
                    # If prompt tokens were not recorded, use data from this event
                    if usage_stats[agent]['prompt_tokens'] == 0:
                        input_tokens = metadata.get('input_tokens', 0)
                        if input_tokens > 0:
                            usage_stats[agent]['prompt_tokens'] += input_tokens
                            usage_stats[agent]['total_tokens'] += input_tokens
            
            # Calculate average latency and tokens per call
            if usage_stats[agent]['n_calls'] > 0:
                usage_stats[agent]['avg_latency'] = usage_stats[agent]['total_latency'] / usage_stats[agent]['n_calls']
                usage_stats[agent]['tokens_per_call'] = usage_stats[agent]['total_tokens'] / usage_stats[agent]['n_calls']
                    
        return usage_stats
    
    def get_error_stats(self) -> Dict[str, Dict[str, Any]]:
        """Analyzes error events.
        
        Returns:
            Error statistics.
        """
        error_stats = {}
        
        for agent, entries in self.agents_data.items():
            error_stats[agent] = {
                'total_errors': 0,
                'error_rate': 0.0,
                'total_operations': 0
            }
            
            for entry in entries:
                # Calculate total number of operations (number of events)
                error_stats[agent]['total_operations'] += 1
                
                # Check for various error conditions
                if entry.get('event') == 'error':
                    error_stats[agent]['total_errors'] += 1
                
                # Check for errors in state updates
                elif entry.get('event') == 'end_node' and entry.get('update', {}).get('error'):
                    error_stats[agent]['total_errors'] += 1
                    
                # Check for tool call errors
                elif entry.get('event') == 'tool_result' and 'error' in str(entry.get('result', '')).lower():
                    error_stats[agent]['total_errors'] += 1
                    
                # Check for LLM exceptions
                elif entry.get('event') == 'llm_exception':
                    error_stats[agent]['total_errors'] += 1
            
            # Calculate error rate
            if error_stats[agent]['total_operations'] > 0:
                error_stats[agent]['error_rate'] = error_stats[agent]['total_errors'] / error_stats[agent]['total_operations']
        
        return error_stats

    def _get_default_tool_stats(self) -> Dict[str, Any]:
        """Returns a default dictionary for tool statistics."""
        return {
            "case_generation_time": 0.0,
            "test_cases_count": 0,
            "successful_cases": 0,
            "failed_cases": 0,
            "success_rate": 0.0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0,
        }

    def analyze_benchmark_logs(self) -> Dict[str, Any]:
        """
        Specifically analyzes benchmark logs, breaking down metrics by major phases:
        1. Test order generation
        2. Test case generation for each tool
        3. Test case execution for each tool
        4. Final report generation
        """
        benchmark_stats = {}
        
        for agent, entries in self.agents_data.items():
            if not agent.startswith("BenchmarkTester-Agent-"):
                continue
                
            report_name = re.sub(r'-\d{4,}.*$', '', agent.replace("BenchmarkTester-Agent-", ""))
            
            # Initialize report structure
            stats = { "phases": {}, "suite_summary": {} }
            
            # Sort by time
            entries = sorted(entries, key=lambda x: x.get('timestamp', ''))
            
            token_usage_map = {e['call_id']: e.get('usage_metadata', {}) for e in entries if e.get('event') == 'llm_token_usage'}
            
            llm_invokes = [e for e in entries if e.get('event') == 'llm_invoke']
            order_gen_call_id = llm_invokes[0]['call_id'] if llm_invokes else None
            report_gen_call_id = llm_invokes[-1]['call_id'] if len(llm_invokes) > 1 else None

            case_gen_invokes = {}
            current_tool_for_gen = None
            for e in entries:
                if e.get("event") == "llm_test_generation_start":
                    current_tool_for_gen = e.get("tool_name")
                if e.get("event") == "llm_invoke" and current_tool_for_gen:
                    if e['call_id'] != order_gen_call_id and e['call_id'] != report_gen_call_id:
                        case_gen_invokes[e['call_id']] = current_tool_for_gen
                        current_tool_for_gen = None 

            for entry in entries:
                event = entry.get("event")
                
                if event == "llm_test_order_generated":
                    phase_name = "1_order_generation"
                    usage = token_usage_map.get(order_gen_call_id, {})
                    stats["phases"][phase_name] = {
                        "duration": entry.get("order_generate_time", 0),
                        "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0), "cost": usage.get("total_cost", 0)
                    }
                
                elif event == "llm_test_case_generated":
                    tool_name = entry.get("tool_name")
                    call_id = next((cid for cid, tname in case_gen_invokes.items() if tname == tool_name), None)
                    phase_name = f"2_case_gen_{tool_name}"
                    usage = token_usage_map.get(call_id, {})
                    stats["phases"][phase_name] = {
                        "duration": entry.get("case_generate_time", 0),
                        "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0), "cost": usage.get("total_cost", 0)
                    }
                
                elif event == "tool_execution_summary":
                    tool_name = entry.get("tool_name")
                    phase_name = f"3_case_exec_{tool_name}"
                    stats["phases"][phase_name] = { "duration": entry.get("tool_all_case_execute_time", 0), "input_tokens": 0, "output_tokens": 0, "cost": 0 }

                elif event == "llm_test_report_generated":
                    phase_name = "4_report_generation"
                    usage = token_usage_map.get(report_gen_call_id, {})
                    stats["phases"][phase_name] = {
                        "duration": entry.get("report_generate_time", 0),
                        "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0), "cost": usage.get("total_cost", 0)
                    }

                elif event == "test_suite_summary":
                    stats["suite_summary"] = {
                        "total_duration": entry.get("duration"), "total_llm_tokens": entry.get("total_llm_tokens"), "total_cost": entry.get("total_cost")
                    }

            # If the suite_summary event does not exist, calculate from the data of each phase
            if not stats.get("suite_summary") and stats.get("phases"):
                total_duration = 0
                total_input_tokens = 0
                total_output_tokens = 0
                total_cost = 0.0
                
                for phase_data in stats["phases"].values():
                    total_duration += phase_data.get("duration", 0)
                    total_input_tokens += phase_data.get("input_tokens", 0)
                    total_output_tokens += phase_data.get("output_tokens", 0)
                    total_cost += phase_data.get("cost", 0)
                    
                stats["suite_summary"] = {
                    "total_duration": total_duration,
                    "total_llm_tokens": total_input_tokens + total_output_tokens,
                    "total_cost": total_cost
                }
            
            benchmark_stats[report_name] = stats
            
        return benchmark_stats

    def create_benchmark_report(self) -> Dict[str, Any]:
        """Creates a report specifically for benchmarks."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'benchmark_results': self.analyze_benchmark_logs()
        }
        return report

    def visualize_benchmark_report(self, report: Dict[str, Any], output_dir: str):
        """Visualizes the benchmark report."""
        os.makedirs(output_dir, exist_ok=True)
        
        benchmark_results = report.get("benchmark_results", {})
        if not benchmark_results:
            print("No benchmark results available for visualization.")
            return

        for report_name, stats in benchmark_results.items():
            phases_data = stats.get("phases", {})
            if not phases_data:
                continue

            # --- 1. Phase Duration Chart (merging gen and exec) ---
            merged_durations = {}
            processed_tools = set()

            for name, data in phases_data.items():
                duration = data.get("duration", 0)
                if name.startswith("1_order_generation"):
                    merged_durations['Order Generation'] = duration
                elif name.startswith("4_report_generation"):
                    merged_durations['Report Generation'] = duration
                else: # Tool-related phases
                    tool_name = None
                    if name.startswith("2_case_gen_"):
                        tool_name = name.replace("2_case_gen_", "")
                    elif name.startswith("3_case_exec_"):
                        tool_name = name.replace("3_case_exec_", "")

                    if tool_name and tool_name not in processed_tools:
                        gen_duration = phases_data.get(f"2_case_gen_{tool_name}", {}).get("duration", 0)
                        exec_duration = phases_data.get(f"3_case_exec_{tool_name}", {}).get("duration", 0)
                        merged_durations[f"Gen & Exec\n{tool_name}"] = gen_duration + exec_duration
                        processed_tools.add(tool_name)
            
            duration_display_phase_names = list(merged_durations.keys())
            phase_durations = list(merged_durations.values())

            plt.figure(figsize=(16, 8))
            plt.bar(duration_display_phase_names, phase_durations, color='#1f77b4')
            plt.ylabel('Time (seconds)')
            plt.title(f'[{report_name}] - Test Phase Duration Distribution')
            plt.xticks(rotation=45, ha="right")
            for i, v in enumerate(phase_durations):
                if v > 0:
                    plt.text(i, v, f"{v:.2f}s", ha='center', va='bottom')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{report_name}_phase_durations.png'))
            plt.close()

            # --- 2. Phase Token Usage Chart (excluding execution phase) ---
            token_phases = {name: data for name, data in phases_data.items() if not name.startswith("3_case_exec")}

            if token_phases:
                token_display_phase_names = [name.split('_', 1)[1].replace('_', ' ').title() for name in token_phases.keys()]
                token_phase_input_tokens = [p.get("input_tokens", 0) for p in token_phases.values()]
                token_phase_output_tokens = [p.get("output_tokens", 0) for p in token_phases.values()]

                plt.figure(figsize=(16, 8))
                x = range(len(token_display_phase_names))
                plt.bar(x, token_phase_input_tokens, width=0.4, label='Input Tokens', color='#ff7f0e')
                plt.bar(x, token_phase_output_tokens, width=0.4, label='Output Tokens', bottom=token_phase_input_tokens, color='#2ca02c')
                plt.ylabel('Token Count')
                plt.title(f'[{report_name}] - Test Phase Token Usage')
                plt.xticks(x, token_display_phase_names, rotation=45, ha="right")
                plt.legend()
                
                # Add total token count at the top of the bar
                for i, (input_val, output_val) in enumerate(zip(token_phase_input_tokens, token_phase_output_tokens)):
                    total_height = input_val + output_val
                    if total_height > 0:
                        plt.text(x[i], total_height, f'{total_height}', ha='center', va='bottom')

                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f'{report_name}_phase_token_usage.png'))
                plt.close()

    def create_academic_report(self) -> Dict[str, Any]:
        """Creates an academic performance report, focusing on academic evaluation metrics.
        
        Returns:
            A dictionary containing academic evaluation metrics.
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'agents': list(self.agents_data.keys()),
        }
        
        # Token Usage Statistics (Key Academic Metric)
        report['token_usage'] = self.compute_llm_usage()
        
        # Execution Time Statistics (Key Academic Metric)
        durations = {}
        for agent in self.agents_data.keys():
            durations[agent] = self.calculate_duration(agent)
            
            # Add average execution time
            if durations[agent]:
                durations[agent]['avg_duration'] = sum(durations[agent].values()) / len(durations[agent])
            else:
                durations[agent]['avg_duration'] = 0
                
        report['execution_times'] = durations
        
        # Tool Call Efficiency (Key Academic Metric)
        report['tool_efficiency'] = self.compute_tool_efficiency()
        
        # Error Statistics (Key Academic Metric)
        report['error_stats'] = self.get_error_stats()
        
        # Benchmark Report
        report['benchmark_report'] = self.create_benchmark_report()
        
        return report
    
    def visualize_academic_metrics(self, output_dir: str = './reports') -> None:
        """Visualizes key academic metrics.
        
        Args:
            output_dir: Directory to output charts.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Get academic metrics
        token_usage = self.compute_llm_usage()
        tool_efficiency = self.compute_tool_efficiency()
        error_stats = self.get_error_stats()
        
        # 1. Token Usage Comparison Chart
        if token_usage:
            agents = list(token_usage.keys())
            prompt_tokens = [data['prompt_tokens'] for data in token_usage.values()]
            completion_tokens = [data['completion_tokens'] for data in token_usage.values()]
            
            plt.figure(figsize=(12, 8))
            x = range(len(agents))
            width = 0.35
            
            plt.bar(x, prompt_tokens, width, label='Prompt Tokens', color='#1f77b4')
            plt.bar([i + width for i in x], completion_tokens, width, label='Completion Tokens', color='#ff7f0e')
            
            plt.xlabel('Agent')
            plt.ylabel('Token Count')
            plt.title('Agent Token Usage Comparison')
            plt.xticks([i + width/2 for i in x], agents, rotation=45)
            
            # Add value labels
            for i, v in enumerate(prompt_tokens):
                plt.text(i, v + 50, str(v), ha='center')
            
            for i, v in enumerate(completion_tokens):
                plt.text(i + width, v + 50, str(v), ha='center')
            
            plt.legend(loc='upper right')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'token_usage_comparison.png'))
        
        # 2. Average Execution Time Comparison Chart
        durations = {}
        for agent in self.agents_data.keys():
            agent_durations = self.calculate_duration(agent)
            if agent_durations:
                durations[agent] = sum(agent_durations.values()) / len(agent_durations)
            else:
                durations[agent] = 0
                
        if durations:
            plt.figure(figsize=(12, 8))
            agents = list(durations.keys())
            avg_durations = list(durations.values())
            
            plt.bar(agents, avg_durations)
            plt.xlabel('Agent')
            plt.ylabel('Average Execution Time (seconds)')
            plt.title('Agent Average Execution Time Comparison')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'avg_execution_time.png'))
        
        # 3. Tool Call Success Rate Comparison Chart
        if tool_efficiency:
            agents = list(tool_efficiency.keys())
            success_rates = [data['success_rate'] * 100 for data in tool_efficiency.values()]
            
            plt.figure(figsize=(12, 8))
            plt.bar(agents, success_rates)
            plt.xlabel('Agent')
            plt.ylabel('Success Rate (%)')
            plt.title('Agent Tool Call Success Rate')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'tool_success_rate.png'))
        
        # 4. Error Rate Comparison Chart
        if error_stats:
            agents = list(error_stats.keys())
            error_rates = [data['error_rate'] * 100 for data in error_stats.values()]
            
            plt.figure(figsize=(12, 8))
            plt.bar(agents, error_rates)
            plt.xlabel('Agent')
            plt.ylabel('Error Rate (%)')
            plt.title('Agent Error Rate')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'error_rates.png'))


if __name__ == "__main__":
    # Example usage
    analyzer = LogAnalyzer()
    analyzer.load_logs()
    
    # Create academic performance report
    report = analyzer.create_academic_report()
    
    # Save report to file
    with open('academic_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\nAcademic analysis report saved to academic_analysis_report.json")
    
    # Create visualization
    analyzer.visualize_academic_metrics() 