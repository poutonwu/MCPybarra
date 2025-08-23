from langgraph.graph import StateGraph, END
from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.mcp_swe_flow.nodes import (
    load_input_node,
    swe_generate_node,
    server_test_node,
    refine_code_node,
    error_handler_node,
    human_confirmation_node,
    error_recovery_node,
    statistics_logger_node
)
from framwork.logger import logger


def create_mcp_swe_workflow():
    """Creates the LangGraph workflow for the MCP agent system."""
    workflow = StateGraph(MCPWorkflowState)

    # Add nodes to the graph
    logger.info("Adding nodes to the graph...")
    workflow.add_node("load_input", load_input_node)
    workflow.add_node("swe_generate", swe_generate_node)
    workflow.add_node("server_test", server_test_node)
    workflow.add_node("refine_code", refine_code_node)
    workflow.add_node("error_handler", error_handler_node)
    workflow.add_node("human_confirmation", human_confirmation_node)
    workflow.add_node("error_recovery", error_recovery_node)
    workflow.add_node("statistics_logger", statistics_logger_node)
    logger.info("Nodes added.")

    # Define the entry point
    workflow.set_entry_point("load_input")
    logger.info("Entry point set to 'load_input'.")

    # Define edges and conditional routing
    logger.info("Defining edges and routing logic...")
    workflow.add_conditional_edges(
        "load_input",
        lambda state: state["next_step"],
        {
            "swe_generate": "swe_generate",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "swe_generate",
        lambda state: state["next_step"],
        {
            "human_confirmation": "human_confirmation",
            "server_test": "server_test",
            "error_handler": "error_handler"
        }
    )
    
    # 从人工确认节点到服务器测试节点
    workflow.add_edge("human_confirmation", "server_test")
    
    workflow.add_conditional_edges(
        "server_test",
        lambda state: state["next_step"],
        {
            "refine_code": "refine_code",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "refine_code",
        lambda state: state["next_step"],
        {            
            "server_test": "server_test",
            "statistics_logger": "statistics_logger",
            "error_handler": "error_handler"
        }
    )

    # Modify the error handler to route to statistics or recovery
    workflow.add_conditional_edges(
        "error_handler",
        lambda state: state["next_step"],
        {
            "statistics_logger": "statistics_logger",
            "error_recovery": "error_recovery"
        }
    )
    
    # Route from error recovery to next steps or statistics
    workflow.add_conditional_edges(
        "error_recovery",
        lambda state: state["next_step"],
        {
            "server_test": "server_test",
            "refine_code": "refine_code",
            "statistics_logger": "statistics_logger"
        }
    )

    # The statistics logger is the final step before the end
    workflow.add_edge("statistics_logger", END)

    logger.info("Edges and routing defined.")

    # Compile the graph
    logger.info("Compiling the graph...")
    app = workflow.compile()
    logger.info("Graph compiled successfully.")
    return app 