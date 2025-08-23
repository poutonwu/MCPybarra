import argparse
import asyncio
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Ensure the working directory is the project root
# and load environment variables from .env file
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
os.chdir(project_root)
load_dotenv()

from framwork.mcp_swe_flow.graph import create_mcp_swe_workflow
from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.mcp_swe_flow.config import llm
from framwork.logger import logger

async def main():
    parser = argparse.ArgumentParser(description="Run the MCP Agent LangGraph workflow.")
    parser.add_argument(
        "--api", 
        required=False, 
        help="Name of the API to process (must match a directory name in resources/)."
    )
    parser.add_argument(
        "--user-input",
        type=str,
        help="Natural language description for generating a custom MCP server."
    )
    # 添加交互式模式选项
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,  # Default to interactive mode
        help="Enable interactive mode, pause at key steps for user confirmation"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Disable interactive mode, workflow will run continuously"
    )
    parser.add_argument(
        "--swe-model",
        type=str,
        default=os.getenv("SWE_AGENT_MODEL", "gpt-4o"),
        help="指定SWE-Agent要使用的LLM模型名称 (例如: gpt-4o, qwen-max, claude-sonnet-4-20250514)"
    )
    # Add other arguments if needed (e.g., --output-dir, --llm-model)
    args = parser.parse_args()
    
    # Handle interactive flags
    interactive_mode = args.interactive and not args.non_interactive
    
    # At least one input method must be provided
    if not args.api and not args.user_input:
        parser.error("Must provide either --api or --user-input parameter")
        sys.exit(1)
        
    # If both inputs are provided, api mode takes priority
    mode = "api" if args.api else "user_input"
    logger.info(f"Starting MCP Agent Workflow in {mode} mode")
    logger.info(f"Interactive mode: {'Enabled' if interactive_mode else 'Disabled'}")
    logger.info(f"Using SWE model: {args.swe_model}")
    
    if mode == "api":
        logger.info(f"Processing API: {args.api}")
    else:
        logger.info(f"Processing user input: {args.user_input[:50]}...")

    # Ensure the workspace directory exists, mirroring the tool's assumption
    workspace_dir = project_root / "workspace"
    workspace_dir.mkdir(exist_ok=True)
    logger.info(f"Ensured workspace directory exists: {workspace_dir}")

    # Create the workflow application
    try:
        app = create_mcp_swe_workflow()
    except Exception as e:
        logger.error(f"Failed to create the workflow graph: {e}")
        sys.exit(1)

    # Define the initial state
    initial_state = {
        "interactive_mode": interactive_mode,  # Add interactive mode setting
        "swe_model": args.swe_model # Pass the selected SWE model to the workflow
    }
    
    # Temporarily override environment variable to ensure command line arguments take priority over environment variables
    original_env_value = os.environ.get("SWE_AGENT_MODEL")
    os.environ["SWE_AGENT_MODEL"] = args.swe_model
    logger.info(f"Temporarily overriding SWE_AGENT_MODEL environment variable: {original_env_value} -> {args.swe_model}")
    
    if args.api:
        initial_state["api_name"] = args.api
    if args.user_input:
        initial_state["user_input"] = args.user_input
    # Directory paths will be set by load_input_node using defaults for now

    logger.info(f"Invoking workflow with initial state: {initial_state}")

    # Invoke the workflow
    try:
        # Configuration for streaming, debugging, etc.
        # config = {"recursion_limit": 10} # Example config
        final_state = await app.ainvoke(initial_state) #, config=config)
        
        logger.info("Workflow invocation complete.")

        # Print the results
        print("\n--- Workflow Finished ---")
        if final_state.get("error"):
            print(f"Status: FAILED")
            print(f"Error: {final_state['error']}")
        else:
            print(f"Status: SUCCESS")
            print(f"Generated Server: {final_state.get('server_file_path')}")
            print(f"Test Report:      {final_state.get('test_report_path')}")
        print("-------------------------")
        
        # Optionally print the full final state for debugging
        # print("\nFinal State:")
        # print(json.dumps(final_state, indent=2))

    except Exception as e:
        logger.error(f"An error occurred during workflow execution: {e}", exc_info=True)
        print(f"\n--- Workflow FAILED --- \nError: {e}\n-------------------------")
        sys.exit(1)
    finally:
        # Restore original environment variable
        if original_env_value:
            os.environ["SWE_AGENT_MODEL"] = original_env_value
        else:
            os.environ.pop("SWE_AGENT_MODEL", None)
        logger.info("Restored original SWE_AGENT_MODEL environment variable")

if __name__ == "__main__":
    asyncio.run(main()) 