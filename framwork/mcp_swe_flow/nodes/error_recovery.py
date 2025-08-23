import datetime
import re
from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.logger import logger

def error_recovery_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """Error recovery node that provides different recovery options based on error source, allowing users to resolve issues and continue the workflow."""
    logger.info("--- Entering Error Recovery Node ---")
    error_source = state.get("error_source", "unknown")
    error_msg = state.get("error", "Unknown error")

    # --- Display error information and general suggestions to user ---
    print("\n" + "="*30)
    print(f"❌ Workflow encountered an error at '{error_source}' node.")
    print(f"   Error details: {error_msg}")
    print("="*30)
    
    print("\n🔍 Troubleshooting suggestions:")
    if "ModuleNotFoundError" in error_msg or "ImportError" in error_msg:
        module_match = re.search(r"No module named '([^']*)'", error_msg)
        missing_module = module_match.group(1) if module_match else "unknown module"
        print(f"  - Seems to be missing Python dependency: '{missing_module}'.")
    elif "Connection closed" in error_msg or "process exited" in error_msg:
        print("  - Server process may have failed to start or crashed unexpectedly.")
        print("    👉 Please check if the generated code has syntax errors or initialization issues.")
        print("    👉 Confirm all required environment variables (such as API keys) are properly set.")
    else:
        print("  - Please check detailed logs in terminal for more clues.")
        print("  - Review generated code or related configuration files.")

    # --- Provide specific recovery options based on error source ---
    if error_source == "server_test":
        print("\n🛠️ How would you like to proceed? (Server test failed)")
        print("  1. Retry test (default option, press Enter directly)")
        print("  2. Skip test, proceed directly to code optimization phase")
        print("  3. Exit workflow")
        
        choice = input("\nYour choice [1]: ").strip().lower()
        
        if choice == "2" or choice == "skip":
            logger.info("User chose to skip test and enter optimization phase.")
            empty_report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "server": state.get("server_file_path", "unknown"),
                "status": "skipped_after_error",
                "message": "User chose to skip test after encountering error at test node.",
                "tests": []
            }
            return {
                **state, 
                "error": None,
                "error_source": None,
                "next_step": "refine_code",
                "test_report_content": empty_report,
            }
        elif choice == "3" or choice == "exit":
            logger.info("User chose to exit workflow.")
            return {**state, "next_step": "end"}
        else:
            logger.info("User chose to retry test.")
            return {**state, "error": None, "error_source": None, "next_step": "server_test"}

    elif error_source == "code_refiner":
        print("\n🛠️ How would you like to proceed? (Code optimization failed)")
        print("  1. Retry optimization (default option, press Enter directly)")
        print("  2. Exit workflow")
        
        choice = input("\nYour choice [1]: ").strip().lower()

        if choice == "2" or choice == "exit":
            logger.info("User chose to exit workflow.")
            return {**state, "next_step": "end"}
        else:
            logger.info("User chose to retry optimization.")
            return {**state, "error": None, "error_source": None, "next_step": "refine_code"}
    
    else:
        logger.warning(f"'{error_source}' has no specific recovery path, workflow will terminate.")
        print("\n" + "!"*60)
        print("! Unknown error source, cannot provide recovery options. Workflow will exit.")
        print("!"*60)
        return {**state, "next_step": "end"} 