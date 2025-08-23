from typing import Dict, List, Optional, Any, TypedDict, Union

class MCPWorkflowState(TypedDict, total=False):
    """
    TypedDict representing the state of the MCP workflow.
    
    This state is passed between nodes in the workflow graph.
    """
    # Input parameters
    api_name: str
    server_file_name: str
    resources_dir: str
    output_dir: str
    refinement_dir: str
    test_report_dir: str
    user_input: str
    model_name: str # The name of the LLM model to use for the run
    
    # Loaded content
    api_spec: Dict[str, Any]
    api_spec_path: str
    mcp_doc: str
    api_doc: Optional[str]
    project_dir: str # Base directory for all outputs of a single run
    refinement_loop_count: int
    
    # Generated content
    server_code: str
    server_file_path: str
    test_report: Union[str, Dict[str, Any]]
    test_report_path: str
    test_report_content: Union[str, Dict[str, Any]]
    refined_code: str
    refined_code_path: str
    refined_report: Dict[str, Any]
    log_files: List[str] # List of paths to agent log files for the current run
    
    # Flow control
    next_step: Optional[str]
    error: Optional[str] 
    error_source: Optional[str]
    
    # 交互控制
    interactive_mode: bool
    human_confirmed: bool 