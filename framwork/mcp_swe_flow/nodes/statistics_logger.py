import json
from pathlib import Path
import traceback

from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.tool import save_file_tool
from framwork.logger import logger, PROJECT_ROOT

async def statistics_logger_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """
    Aggregates token usage and cost statistics from all agent log files
    generated during the workflow run and saves a final report.
    """
    logger.info("--- 📊 Starting Statistics Logger Node ---")
    
    log_files = state.get("log_files", [])
    project_dir_str = state.get("project_dir")
    
    # Ensure project_dir is valid, otherwise, we can't save the report.
    if not project_dir_str:
        logger.error("Cannot generate statistics report: 'project_dir' is missing from the state.")
        # This isn't a critical error for the whole flow, so we proceed to the end.
        return {**state, "next_step": "end"}

    project_dir = Path(project_dir_str)
        
    if not log_files:
        logger.warning("No log files were found in the state to generate statistics from.")
        # Still generate an empty report for consistency
        report_content = "# Statistics Report\n\nNo log files found to analyze.\n"
    else:
        logger.info(f"Aggregating statistics from {len(log_files)} log file(s)...")
        
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0
        total_cost = 0.0
        model_usage = {}
        total_tool_calls = 0
        tool_usage_counts = {}

        unique_log_files = sorted(list(set(log_files)))
        
        for log_path_str in unique_log_files:
            log_path = Path(log_path_str)
            if not log_path.exists():
                logger.warning(f"Log file not found: {log_path}")
                continue
            
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line)
                            # Per user feedback, we only observe the 'llm_response' event,
                            # as it marks the definitive end of a single LLM invocation.
                            if log_entry.get("event") == "llm_response":
                                metadata = log_entry.get("usage_metadata", {})
                                if not metadata:
                                    continue

                                model = metadata.get("model", "unknown")
                                prompt_tokens = metadata.get("input_tokens", 0)
                                completion_tokens = metadata.get("output_tokens", 0)
                                # The 'llm_response' event uses the 'cost' key for the total cost.
                                cost = metadata.get("cost", 0.0)
                                
                                # Aggregate totals
                                total_prompt_tokens += prompt_tokens
                                total_completion_tokens += completion_tokens
                                total_cost += cost

                                # Aggregate per-model stats
                                if model not in model_usage:
                                    model_usage[model] = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0, "calls": 0}
                                
                                model_usage[model]["prompt_tokens"] += prompt_tokens
                                model_usage[model]["completion_tokens"] += completion_tokens
                                model_usage[model]["cost"] += cost
                                model_usage[model]["calls"] += 1
                                
                            # Also, capture tool call events
                            elif log_entry.get("event") == "tool_call":
                                tool_name = log_entry.get("tool", "unknown_tool")
                                total_tool_calls += 1
                                tool_usage_counts[tool_name] = tool_usage_counts.get(tool_name, 0) + 1
                                
                        except (json.JSONDecodeError, KeyError):
                            # Ignore lines that are not valid JSON or don't have the expected keys
                            continue
            except Exception as e:
                logger.error(f"Failed to read or process log file {log_path}: {e}")

        total_tokens = total_prompt_tokens + total_completion_tokens

        # --- Format the report ---
        report_content = f"""# Workflow Execution Statistics

## 概要

| 指标 | 数值 |
| :--- | :--- |
| **总 Token 消耗** | **{total_tokens:,}** |
| **总预估成本 (RMB)** | **¥{total_cost:.6f}** |
| **总工具调用次数** | **{total_tool_calls}** |
| 提示 Token | {total_prompt_tokens:,} |
| 完成 Token | {total_completion_tokens:,} |

---

## 按模型划分的使用情况

"""
        if not model_usage:
            report_content += "没有找到任何模型的 LLM 调用记录。\n"
        else:
            for model, usage in sorted(model_usage.items()):
                report_content += f"""
### 模型: `{model}`

| 指标 | 数值 |
| :--- | :--- |
| **总调用次数** | **{usage['calls']}** |
| **总成本 (RMB)** | **¥{usage['cost']:.6f}** |
| 总 Token | {usage['prompt_tokens'] + usage['completion_tokens']:,} |
| 提示 Token | {usage['prompt_tokens']:,} |
| 完成 Token | {usage['completion_tokens']:,} |
"""
        
        report_content += "\n---\n\n## 按工具划分的使用情况\n\n"
        if not tool_usage_counts:
            report_content += "没有找到任何工具调用记录。\n"
        else:
            report_content += "| 工具名称 | 调用次数 |\n"
            report_content += "| :--- | :--- |\n"
            for tool_name, count in sorted(tool_usage_counts.items()):
                report_content += f"| `{tool_name}` | {count} |\n"

        logger.info(f"Generated statistics summary: Total Tokens={total_tokens}, Total Cost=¥{total_cost:.6f}, Total Tool Calls={total_tool_calls}")

    # --- Save the report ---
    try:
        report_file_name = "statistics_report.md"
        # The save_file_tool expects a path relative to its workspace root (PROJECT_ROOT/workspace)
        workspace_dir = PROJECT_ROOT / "workspace"
        
        # Ensure the project directory path is absolute before making it relative
        if not project_dir.is_absolute():
            project_dir = workspace_dir / project_dir
            
        relative_report_path = project_dir.relative_to(workspace_dir) / report_file_name
        
        await save_file_tool.ainvoke({
            "file_path": str(relative_report_path),
            "content": report_content
        })
        absolute_report_path = project_dir / report_file_name
        logger.info(f"✅ Statistics report saved to: {absolute_report_path}")

    except Exception as e:
        logger.error(f"Failed to save statistics report: {e}\n{traceback.format_exc()}")
        # The flow should still end gracefully even if the report fails to save
        
    update = {
        "next_step": "end"
    }
    
    logger.info("--- ✅ Statistics Logger Node Completed ---")
    return {**state, **update} 