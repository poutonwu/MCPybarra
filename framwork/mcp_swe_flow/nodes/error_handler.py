from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.logger import logger

def error_handler_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """Handle workflow errors, decide whether to enter recovery node or terminate workflow based on error source."""
    logger.error("--- Entering Error Handler Node ---")
    error_msg = state.get('error', 'Unknown error')
    error_source = state.get('error_source', 'unknown')
    logger.error(f"Workflow failed with error from '{error_source}': {error_msg}")
    
    # Errors from server_test or code_refiner should enter recovery process
    if error_source in ["server_test", "code_refiner"]:
        logger.info(f"Error from '{error_source}' detected, routing to error recovery node.")
        return {**state, "next_step": "error_recovery"}
    
    # Errors from other sources (e.g., from load_input or swe_generate) will terminate workflow
    logger.error(f"Unhandled error source ('{error_source}'), terminating workflow.")
    update = {"next_step": "end"} # Ensure workflow termination
    return {**state, **update} 