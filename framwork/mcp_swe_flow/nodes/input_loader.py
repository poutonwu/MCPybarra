from pathlib import Path

# Corrected imports for the new structure
from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.mcp_swe_flow.utils import find_api_file, load_api_spec, load_mcp_doc
from framwork.mcp_swe_flow.config import (
    DEFAULT_RESOURCES_DIR, 
    DEFAULT_OUTPUT_DIR, 
    DEFAULT_REFINEMENT_DIR, 
    DEFAULT_TEST_REPORT_DIR
)
from framwork.logger import logger, get_agent_logger


def load_input_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """
    Loads initial inputs like API name, specification, and MCP documentation.
    Initializes paths for directories.
    
    Supports two modes:
    1. API mode: Loads API specifications from a given API name
    2. User input mode: Uses natural language user input to generate a custom MCP server
    """
    agent_logger = get_agent_logger("InputLoader-Agent")
    logger.info("--- Starting Load Input Node ---")
    agent_logger.log(event_type="start_node", state=state)
    api_name = state.get("api_name")
    user_input = state.get("user_input")
    print(user_input)
    
    mode = "api" if api_name else "user_input" if user_input else None
    agent_logger.log(event_type="mode_decision", mode=mode)
    
    # Initialize directory paths using defaults if not provided
    resources_dir = Path(state.get("resources_dir", DEFAULT_RESOURCES_DIR))
    output_dir = Path(state.get("output_dir", DEFAULT_OUTPUT_DIR))
    refinement_dir = Path(state.get("refinement_dir", DEFAULT_REFINEMENT_DIR))
    test_report_dir = Path(state.get("test_report_dir", DEFAULT_TEST_REPORT_DIR))
    
    # Create directories if they don't exist
    # These should be relative to the workspace root handled by tools/nodes as needed
    # The LangchainFileSaverTool uses workspace_root = Path("workspace") 
    # Ensure consistency or adjust tool/node logic if paths are meant differently
    (Path("workspace") / "output-servers").mkdir(parents=True, exist_ok=True)
    (Path("workspace") / "refinement").mkdir(parents=True, exist_ok=True)
    (Path("workspace") / "server-test-report").mkdir(parents=True, exist_ok=True)
    
    update: dict = {
        # Keep critical state from the initial call
        "swe_model": state.get("swe_model"),
        "interactive_mode": state.get("interactive_mode", True),

        # Store absolute paths derived from defaults or state
        "resources_dir": str(resources_dir.resolve()), 
        "output_dir": str(output_dir.resolve()),
        "refinement_dir": str(refinement_dir.resolve()),
        "test_report_dir": str(test_report_dir.resolve()),
        "error": None, # Clear previous errors
        "next_step": None, # Clear previous step directive
    }

    if not mode:
        logger.error("必须提供API名称或用户输入。")
        agent_logger.log(event_type="error", error="必须提供API名称（api_name）或用户输入（user_input）。", state=state)
        update["error"] = "必须提供API名称（api_name）或用户输入（user_input）。"
        update["next_step"] = "error_handler" 
        return {**state, **update}
    
    logger.info(f"运行模式: {mode}")

    # Load MCP Document (using the potentially resolved resources_dir)
    mcp_doc = load_mcp_doc(Path(update["resources_dir"]))
    if not mcp_doc:
        update["error"] = f"Failed to load MCP documentation from {update['resources_dir']}"
        update["next_step"] = "error_handler"
        agent_logger.log(event_type="error", error=update["error"], state=state)
        return {**state, **update}
    update["mcp_doc"] = mcp_doc

    if mode == "api":
        api_spec_path = find_api_file(Path(update["resources_dir"]), api_name)
        if not api_spec_path:
            update["error"] = f"Could not find OpenAPI spec file for API '{api_name}' in {update['resources_dir']}"
            update["next_step"] = "error_handler"
            agent_logger.log(event_type="error", error=update["error"], state=state)
            return {**state, **update}
        update["api_spec_path"] = str(api_spec_path)

        api_spec = load_api_spec(api_spec_path)
        if not api_spec:
            update["error"] = f"Failed to load API specification from {api_spec_path}"
            update["next_step"] = "error_handler"
            agent_logger.log(event_type="error", error=update["error"], state=state)
            return {**state, **update}
        update["api_spec"] = api_spec
        logger.info(f"已成功加载API '{api_name}' 的规范")
        agent_logger.log(event_type="api_loaded", api_name=api_name, api_spec_path=str(api_spec_path))
    else:
        if not user_input or len(user_input.strip()) < 10:  
            update["error"] = "用户输入为空或过短。请提供详细的描述。"
            update["next_step"] = "error_handler"
            agent_logger.log(event_type="error", error=update["error"], state=state)
            return {**state, **update}
        logger.info("用户输入模式：已验证用户输入")
        agent_logger.log(event_type="user_input_validated", user_input=user_input)

    # Determine the next step after successful loading
    update["next_step"] = "swe_generate" 
    logger.info(f"Successfully loaded inputs for {mode} mode")
    agent_logger.log(event_type="node_success", mode=mode, update=update)
    logger.info("--- Finished Load Input Node ---")
    return {**state, **update} 