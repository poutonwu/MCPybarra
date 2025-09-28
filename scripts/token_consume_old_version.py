import os
import json
import re
from pathlib import Path
from collections import defaultdict
import datetime
from typing import Dict, Any, Optional

# --- Configuration ---
# Define paths relative to the script's location or a fixed project root
try:
    PROJECT_ROOT = Path(__file__).parent.parent
except NameError:
    PROJECT_ROOT = Path().resolve()

WORKSPACE_DIR = PROJECT_ROOT / "workspace"
LOGS_DIR = PROJECT_ROOT / "logs" / "agent_logs"
DATA_DIR = PROJECT_ROOT / "data" / "summary_data"

REFINEMENT_DIR = WORKSPACE_DIR / "refinement"
OUTPUT_FILE = DATA_DIR / "old_version_token_consumption_report.md"

# --- Cost Calculation Logic (copied from framwork/mcp_swe_flow/config/config.py) ---
MODEL_CONFIG = {
    # Qwen models via Dashscope
    r"^qwen-": {
        "provider": "qwen",
        "costs": {
            "qwen-max": {"prompt": 0.0000024, "completion": 0.0000096},
            "qwen-max-latest": {"prompt": 0.0000024, "completion": 0.0000096},
            "qwen-plus": {"prompt": 0.0000008, "completion": 0.000002},
            "default": {"prompt": 0.0000024, "completion": 0.0000096}
        }
    },
    # Deepseek models
    r"^deepseek-": {
        "provider": "deepseek",
        "costs": {
            "deepseek-chat": {"prompt": 0.000002, "completion": 0.000008},
            "default": {"prompt": 0.000015, "completion": 0.00003}
        }
    },
    # Models via GPTSAPI (ChatGPT, Claude)
    r"^(gpt|claude)-": {
        "provider": "gptsapi",
        "costs": {
            "claude-sonnet-4-20250514": {"prompt": 0.00002376, "completion": 0.0001188},
            "gpt-4o": {"prompt": 0.000018, "completion": 0.000072},
            "gemini-2.5-pro-preview-03-25": {"prompt": 0.00000138, "completion": 0.000011},
            "default": {"prompt": 0.00002, "completion": 0.00006}
        }
    },
    # Gemini models
    r"^gemini-": {
        "provider": "gemini",
        "costs": {
            "gemini-2.5-pro": {"prompt": 0.00000138, "completion": 0.000011},
            "default": {"prompt": 0.0000025, "completion": 0.000005}
        }
    },
    # Default fallback for any other model
    "default": {
        "provider": "default",
        "costs": {
            "default": {"prompt": 0.0000008, "completion": 0.000002}
        }
    }
}

def get_provider_config(model_name: str):
    """Finds the provider configuration for a given model name."""
    for pattern, config in MODEL_CONFIG.items():
        if pattern != "default" and re.match(pattern, model_name):
            return config
    return MODEL_CONFIG["default"]

def calculate_cost(model_name: str, prompt_tokens: int, completion_tokens: int):
    """Calculates the token cost for a given model."""
    if not model_name:
        model_name = "unknown"
    provider_config = get_provider_config(model_name)
    model_cost_config = provider_config["costs"]
    
    costs = model_cost_config.get(model_name, model_cost_config["default"])
    
    prompt_cost = prompt_tokens * costs["prompt"]
    completion_cost = completion_tokens * costs["completion"]
    total_cost = prompt_cost + completion_cost
    
    return {
        "prompt_cost": prompt_cost,
        "completion_cost": completion_cost,
        "total_cost": total_cost
    }

# --- Main Analysis Logic ---
def parse_date_from_filename(filename: str) -> datetime.date | None:
    """
    Extracts a datetime.date object from a log filename.
    Handles filenames like: 'Agent-project-name-YYYYMMDDTHHMMZ.jsonl'
    """
    match = re.search(r'-(\d{4})(\d{2})(\d{2})T', filename)
    if match:
        year, month, day = map(int, match.groups())
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None # Invalid date like month 13, etc.
    return None

def parse_agent_from_filename(filename: str) -> Optional[str]:
    """Extracts agent type from filename."""
    if filename.startswith("SWE-Agent"):
        return "SWE-Agent"
    if filename.startswith("ServerTest-Agent"):
        return "ServerTest-Agent"
    if filename.startswith("CodeRefiner-Agent"):
        return "CodeRefiner-Agent"
    return None

def parse_timestamp(ts_str: str) -> Optional[datetime.datetime]:
    """Parses a timestamp string into a datetime object."""
    try:
        # Handle potential floating point seconds and the 'Z' suffix
        return datetime.datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None

def get_start_time(log_file: Path) -> Optional[datetime.datetime]:
    """Reads the first line of a log file to get its start timestamp."""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line:
                log_entry = json.loads(first_line)
                return parse_timestamp(log_entry.get("timestamp"))
    except (IOError, json.JSONDecodeError):
        return None
    return None

def analyze_logs():
    """
    Analyzes agent logs to calculate token consumption and cost for projects
    found in the refinement directory. It only considers the latest log run
    for each project that occurred before July 1st of the run's year.
    """
    if not REFINEMENT_DIR.is_dir():
        print(f"Error: Refinement directory not found at '{REFINEMENT_DIR}'")
        return

    project_stats = defaultdict(lambda: {
        "agents": {
            "SWE-Agent": defaultdict(float),
            "ServerTest-Agent": defaultdict(float),
            "CodeRefiner-Agent": defaultdict(float),
        }
    })

    project_dirs = [d for d in REFINEMENT_DIR.iterdir() if d.is_dir()]
    
    for project_dir in project_dirs:
        # e.g., "zotero_mcp_server_refined" -> "zotero_mcp_server"
        base_name = project_dir.name.replace("_refined", "")
        print(f"Processing project: {base_name}")

        # Find all log files for this project, regardless of date
        all_project_files = list(LOGS_DIR.glob(f"*-{base_name}-*.jsonl"))

        if not all_project_files:
            print(f"  - No log files with strict name match '{base_name}' found.")
            continue

        # Get start times for all found logs
        files_with_start_times = []
        for log_file in all_project_files:
            start_time = get_start_time(log_file)
            if start_time:
                files_with_start_times.append({"file": log_file, "time": start_time})
        
        if not files_with_start_times:
            print(f"  - Could not read start times from any log files for this project.")
            continue
            
        # Sort all files chronologically
        files_with_start_times.sort(key=lambda x: x["time"])

        # Cluster all files into runs
        runs = []
        if files_with_start_times:
            current_run = [files_with_start_times[0]]
            for i in range(1, len(files_with_start_times)):
                prev_file_time = files_with_start_times[i-1]["time"]
                current_file_time = files_with_start_times[i]["time"]
                
                # If time gap is more than 60 minutes, it's a new run
                if current_file_time - prev_file_time > datetime.timedelta(minutes=60):
                    runs.append(current_run)
                    current_run = [] # Start a new run
                current_run.append(files_with_start_times[i])
            runs.append(current_run) # Add the last run

        if not runs:
            print(f"  - Failed to cluster log files into runs.")
            continue

        # Find the latest valid run (started before the cutoff date)
        latest_valid_run_files = None
        
        # Special handling for mcp_word_processor as per user request
        project_specific_cutoff = None
        if base_name == "mcp_word_processor":
            project_specific_cutoff = datetime.datetime(2025, 6, 28, 16, 0, 0, tzinfo=datetime.timezone.utc)

        for run in reversed(runs):
            run_start_time = run[0]["time"]

            # Determine the cutoff date for the current run
            cutoff_date = project_specific_cutoff or datetime.datetime(run_start_time.year, 7, 1, tzinfo=datetime.timezone.utc)
            
            if run_start_time < cutoff_date:
                # This is the run we want to analyze
                latest_valid_run_files = [item["file"] for item in run]
                run_start_date_str = run_start_time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"  - Analyzing latest valid run starting on {run_start_date_str}. Found {len(latest_valid_run_files)} log file(s) in this run.")
                if project_specific_cutoff:
                    print(f"    (Used project-specific cutoff: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})")
                break # Stop after finding the first valid run from the end
        
        if not latest_valid_run_files:
            print(f"  - No runs found that started before July 1st for this project.")
            continue
            
        # Analyze the selected log files
        for log_file in latest_valid_run_files:
            agent_type = parse_agent_from_filename(log_file.name)
            if not agent_type:
                continue
            
            print(f"    - Parsing {log_file.name} for agent {agent_type}")
            
            # --- Per-file duration calculation ---
            file_timestamps = []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        
                        # Store all timestamps for this file
                        ts = parse_timestamp(log_entry.get("timestamp"))
                        if ts:
                            file_timestamps.append(ts)

                        # Only consider 'llm_response' events to avoid double counting
                        if log_entry.get("event") == "llm_response":
                            usage_metadata = log_entry.get("usage_metadata", {})
                            if not usage_metadata:
                                continue

                            model = usage_metadata.get("model", "unknown")
                            prompt_tokens = usage_metadata.get("input_tokens", 0)
                            completion_tokens = usage_metadata.get("output_tokens", 0)
                            
                            if prompt_tokens == 0 and completion_tokens == 0:
                                continue

                            costs = calculate_cost(model, prompt_tokens, completion_tokens)
                            
                            current_agent_stats = project_stats[base_name]["agents"][agent_type]
                            current_agent_stats["prompt_tokens"] += prompt_tokens
                            current_agent_stats["completion_tokens"] += completion_tokens
                            current_agent_stats["total_tokens"] += (prompt_tokens + completion_tokens)
                            current_agent_stats["total_cost"] += costs["total_cost"]
                    
                    except (json.JSONDecodeError, KeyError):
                        # Ignore lines that are not valid JSON or don't have the expected structure
                        pass
            
            # Calculate and accumulate duration for this specific file
            if file_timestamps:
                min_ts = min(file_timestamps)
                max_ts = max(file_timestamps)
                duration_seconds = (max_ts - min_ts).total_seconds()
                project_stats[base_name]["agents"][agent_type]["duration"] = project_stats[base_name]["agents"][agent_type].get("duration", 0) + duration_seconds

    # 5. Generate and save the report
    generate_report(project_stats)


def generate_report(project_stats: Dict[str, Any]):
    """Generates a detailed markdown report with per-agent stats."""
    report_lines = [
        "# Old Version Token & Time Consumption Report",
        f"Generated on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Note: Costs are calculated in RMB (¥).",
        "\n"
    ]

    if not project_stats:
        report_lines.append("No projects found or no token usage data could be analyzed.")
        full_report = "\n".join(report_lines)
        print(full_report)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(full_report)
        return

    grand_total_tokens = 0
    grand_total_cost = 0.0
    grand_total_duration = 0.0

    sorted_projects = sorted(project_stats.items(), key=lambda item: item[0])

    for project_name, data in sorted_projects:
        report_lines.append(f"## Project: `{project_name}`\n")
        report_lines.append("| Stage               | Prompt Tokens | Completion Tokens | Total Tokens | Total Cost (RMB) | Time Taken (s) |")
        report_lines.append("|---------------------|---------------|-------------------|--------------|------------------|----------------|")
        
        project_total_prompt = 0
        project_total_completion = 0
        project_total_tokens = 0
        project_total_cost = 0.0
        project_total_duration = 0.0

        for agent_type in ["SWE-Agent", "ServerTest-Agent", "CodeRefiner-Agent"]:
            stats = data["agents"][agent_type]
            prompt = int(stats.get('prompt_tokens', 0))
            completion = int(stats.get('completion_tokens', 0))
            total_tokens = int(stats.get('total_tokens', 0))
            cost = stats.get('total_cost', 0.0)
            duration = stats.get('duration', 0.0)

            report_lines.append(
                f"| {agent_type:<19} | {f'{prompt:,}'.rjust(13)} | {f'{completion:,}'.rjust(17)} | {f'{total_tokens:,}'.rjust(12)} | ¥{f'{cost:.4f}'.rjust(15)} | {f'{duration:.2f}'.rjust(14)} |"
            )
            
            project_total_prompt += prompt
            project_total_completion += completion
            project_total_tokens += total_tokens
            project_total_cost += cost
            project_total_duration += duration

        report_lines.append("|---------------------|---------------|-------------------|--------------|------------------|----------------|")
        report_lines.append(
            f"| **Project Total**   | **{f'{project_total_prompt:,}'.rjust(9)}** | **{f'{project_total_completion:,}'.rjust(11)}** | **{f'{project_total_tokens:,}'.rjust(8)}** | **¥{f'{project_total_cost:.4f}'.rjust(13)}** | **{f'{project_total_duration:.2f}'.rjust(12)}** |"
        )
        report_lines.append("\n---\n")

        grand_total_tokens += project_total_tokens
        grand_total_cost += project_total_cost
        grand_total_duration += project_total_duration
    
    report_lines.append(f"## Grand Totals\n")
    report_lines.append(f"- **Total Projects Analyzed:** {len(project_stats)}")
    report_lines.append(f"- **Grand Total Tokens:** {int(grand_total_tokens):,}")
    report_lines.append(f"- **Grand Total Cost:** ¥{grand_total_cost:.4f}")
    report_lines.append(f"- **Grand Total Duration (seconds):** {grand_total_duration:,.2f}")

    full_report = "\n".join(report_lines)
    
    print("--- Analysis Complete ---")
    print(full_report)
    
    DATA_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    analyze_logs()
