#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for testing imports of framework-related packages
Used to ensure that system paths are set correctly and required modules can be imported properly
"""

import os
import sys
import importlib
import traceback
from dotenv import load_dotenv

# Add project root directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added project root directory to system path: {project_root}")

# Load .env file
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f"✅ Environment variables loaded: {dotenv_path}")
else:
    print(f"⚠️  .env file not found: {dotenv_path}, some features may not work properly.")

def test_imports():
    """Test importing framework-related packages"""
    imports = [
        "framwork.mcp_swe_flow.config",
        "framwork.logger",
        "framwork.mcp_swe_flow.adapters",
        "framwork.tool.langchain_file_reader"
    ]
    
    success_count = 0
    failed_imports = []
    
    for module_path in imports:
        try:
            module = importlib.import_module(module_path)
            print(f"✅ Successfully imported: {module_path}")
            success_count += 1
        except Exception as e:
            print(f"❌ Import failed: {module_path}")
            print(f"   Error message: {str(e)}")
            failed_imports.append((module_path, str(e)))
    
    print(f"\nImport test results: {success_count}/{len(imports)} successful")
    
    if failed_imports:
        print("\nFailed import details:")
        for module_path, error in failed_imports:
            print(f"- {module_path}: {error}")
    
    return success_count == len(imports)

def get_module_objects():
    """Get objects from successfully imported modules"""
    try:
        # Try to import and get LLM
        from framwork.mcp_swe_flow.config import get_llm_for_agent
        llm = get_llm_for_agent("ImportTest-Agent")
        print(f"LLM type: {type(llm).__name__ if llm else 'None'}")
        
        # Try to import and get logger
        from framwork.logger import get_agent_logger
        logger = get_agent_logger("ImportTest-Agent")
        print(f"Logger type: {type(logger).__name__ if logger else 'None'}")
        
        # Try to import and initialize MCP adapter
        from framwork.mcp_swe_flow.adapters.mcp_client_adapter import MCPClientAdapter
        adapter = MCPClientAdapter()
        print(f"MCP adapter type: {type(adapter).__name__ if adapter else 'None'}")
        
        # Try to import and initialize file reader tool
        from framwork.tool.langchain_file_reader import LangchainFileReaderTool
        file_reader = LangchainFileReaderTool()
        print(f"File reader tool type: {type(file_reader).__name__ if file_reader else 'None'}")
        
        return True
    except Exception as e:
        print(f"Failed to get module objects: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("===== Starting framework package import test =====")
    import_success = test_imports()
    
    if import_success:
        print("\n===== Starting module object test =====")
        get_module_objects()
    
    print("\n===== Test completed =====") 