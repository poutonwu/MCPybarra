from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.logger import logger

def human_confirmation_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """Node that waits for user confirmation to continue the workflow, allowing users to make necessary preparations before testing"""
    logger.info("Entering human confirmation node")
    
    print("\n" + "="*50)
    print(f"✅ MCP server code has been generated: {state.get('server_file_path')}")
    print("\nYou can now perform the following operations:")
    print("- Review the generated code")
    print("- Add required API keys")
    print("- Install missing library dependencies")
    
    # Extract and display possible dependencies
    try:
        with open(state.get('server_file_path'), 'r', encoding='utf-8') as f:
            code = f.read()
            imports = [line.strip() for line in code.split('\n') 
                      if line.strip().startswith(('import ', 'from ')) and 'import' in line]
            if imports:
                print("\nPossible dependencies:")
                for imp in imports[:10]:  # Only show first 10
                    print(f"  {imp}")
                if len(imports) > 10:
                    print(f"  ...and {len(imports)-10} more imports...")
    except Exception as e:
        print(f"Unable to parse imports in code: {e}")
        logger.error(f"Unable to parse imports in code: {e}")
    
    input("\nWhen ready, press Enter to continue...")
    logger.info("User has confirmed to continue workflow")
    
    # Ensure all state is passed down
    update = state.copy()
    update.update({
        "next_step": "server_test",
        "human_confirmed": True
    })
    return update 