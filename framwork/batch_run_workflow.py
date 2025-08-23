import argparse
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure the working directory is the project root
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.append(str(project_root))

# A simple logger, as we are in a separate script.
def log(message):
    """A simple logger for printing timestamped messages to console."""
    print(f"[{datetime.now().isoformat()}] {message}")

async def run_workflow(semaphore, user_input, log_dir, swe_model=None):
    """
    Run a single workflow instance for a given user input.
    """
    log(f"⚠️ Batch generation mode can only use --non-interactive, meaning code cannot be adjusted in real-time. For functions involving sensitive information or path information, it's recommended to run run_langgraph_workflow.py.")
    async with semaphore:
        # Create a unique name for the log file to avoid conflicts
        input_slug = "".join(filter(str.isalnum, user_input))[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        log_file_name = f"run_{timestamp}_{input_slug}.log"
        log_file = log_dir / log_file_name
        
        model_info = f"Using model: '{swe_model}'" if swe_model else "Using default model"
        log(f"Starting workflow, {model_info}, input: '{user_input[:40]}...'. Log file: {log_file.name}")
        
        # Dynamically build the command
        command = [
            sys.executable,  # Use the same python interpreter
            "framwork/run_langgraph_workflow.py",
        ]

        if swe_model:
            command.extend(["--swe-model", swe_model])
        
        command.extend([
            "--user-input",
            user_input,
            "--non-interactive"
        ])

        # Redirect subprocess stdout/stderr to log file
        with open(log_file, "w", encoding="utf-8") as log_output:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=log_output,
                stderr=asyncio.subprocess.STDOUT
            )

        await process.wait()

        if process.returncode == 0:
            log(f"✅ Success: Workflow '{user_input[:40]}...' completed.")
        else:
            log(f"❌ Failed: Workflow '{user_input[:40]}...' failed. See log for details: {log_file}")
        
        return process.returncode

async def main():
    parser = argparse.ArgumentParser(
        description="Batch run MCP Agent LangGraph workflows from file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input-file",
        default="framwork/batch_inputs.txt",
        help="Path to text file containing one user input per line.\nDefault: framwork/batch_inputs.txt"
    )
    parser.add_argument(
        "-n", "--parallel-runs",
        type=int,
        default=3,
        help="Number of workflows to run in parallel (default: 3)."
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs/batch_runs",
        help="Directory to store logs for each workflow run (default: logs/batch_runs)."
    )
    parser.add_argument(
        "--swe-model",
        type=str,
        default=None,
        help="Specify model for SWE-Agent (e.g., 'deepseek-r1-0528')."
    )
    
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    input_file_path = Path(args.input_file)
    if not input_file_path.is_file():
        log(f"❌ Error: Input file not found at '{args.input_file}'")
        sys.exit(1)

    with open(input_file_path, "r", encoding="utf-8") as f:
        user_inputs = [line.strip() for line in f if line.strip()]

    if not user_inputs:
        log("Input file is empty, no operations to perform.")
        sys.exit(0)

    log(f"Found {len(user_inputs)} user inputs in file '{args.input_file}'.")
    log(f"Will run {args.parallel_runs} workflows in parallel.")
    log(f"Logs will be stored at: {log_dir.resolve()}")
    
    if args.swe_model:
        log(f"Will use SWE Agent model for all workflows: {args.swe_model}")
    
    semaphore = asyncio.Semaphore(args.parallel_runs)
    tasks = [run_workflow(semaphore, user_input, log_dir, args.swe_model) for user_input in user_inputs]
    
    log("\n--- Starting batch processing ---")
    results = await asyncio.gather(*tasks)

    successful_runs = sum(1 for r in results if r == 0)
    failed_runs = len(results) - successful_runs

    log("\n--- Batch processing completed ---")
    log(f"Total workflows executed: {len(results)}")
    log(f"  - Successful: {successful_runs}")
    log(f"  - Failed: {failed_runs}")
    log(f"Logs stored at: {log_dir.resolve()}")
    log("--------------------")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main()) 