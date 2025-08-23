import os
import sys
import json
import time
import subprocess
import re
import glob
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import httpx
from pathlib import Path
import importlib.util
import asyncio

# Ensure we can import other modules from the project by adding the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from testSystem.prompts.utils import load_prompt
# Import custom timeout exception
from testSystem.exceptions import ToolTimeoutError

# MCP相关导入
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# langchain_mcp_adapters相关导入
from langchain_mcp_adapters.tools import load_mcp_tools

# Add Chinese font support
import matplotlib as mpl
from testSystem.reporting import Reporter, SCORE_DIMENSIONS, SCORE_WEIGHTS

# Set Chinese fonts
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif'] 
# Fix the issue where minus sign '-' displays as a square
plt.rcParams['axes.unicode_minus'] = False

# Import LLM-related modules
try:
    from framwork.mcp_swe_flow.config import get_llm_for_agent
    from framwork.logger import logger, get_agent_logger
    # Import file reading tool
    from framwork.tool.langchain_file_reader import LangchainFileReaderTool
    # Import custom tool manager class, not instance
    from framwork.mcp_swe_flow.adapters.tool_manager import MCPToolManager

except ImportError:
    print("Warning: Unable to import framwork modules, will run with basic functionality")
    get_llm_for_agent = None
    logger = None
    get_agent_logger = None
    LangchainFileReaderTool = None

class MCPIntelligentTester:
    """MCP server intelligent testing tool that dynamically constructs test requests based on tool descriptions"""
    
    def __init__(self, output_dir: str = "./server-test-report/", test_files_dir: str = None, **kwargs):
        """Initialize MCP server tester
        
        Args:
            output_dir: Test report output directory
            test_files_dir: Test files directory path, if provided will use this path instead of LangchainFileReaderTool
            **kwargs: Other parameters
                - project_name_override: Project name override
                - tool_timeout: Tool execution timeout (seconds), default 40 seconds
                - max_consecutive_timeouts: Maximum consecutive timeout count, default 3
        """
        self.output_dir = output_dir
        self.test_files_dir = test_files_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Receive project name from external input
        self.project_name_override = kwargs.get("project_name_override")
        
        # Configure timeout parameters
        self.tool_timeout = kwargs.get("tool_timeout", 40.0)  # Default 40 seconds
        self.max_consecutive_timeouts = kwargs.get("max_consecutive_timeouts", 3)  # Default 3 times
        
        # Initialize LLM and logger (will be moved to execution stage)
        self.llm = None
        self.agent_logger = None
        
        # Create an independent tool manager for each tester instance
        self.tool_manager = MCPToolManager()
        
        # Initialize result storage
        self.benchmark_results = {}
        
        # Initialize tool list
        self.tools = []
        
        # Initialize file reading tool
        try:
            if LangchainFileReaderTool:
                self.file_reader_tool = LangchainFileReaderTool()
                print("Successfully initialized file reading tool")
            else:
                self.file_reader_tool = None
                print("Warning: LangchainFileReaderTool not available")
        except Exception as e:
            self.file_reader_tool = None
            print(f"Failed to initialize file reading tool: {str(e)}")
        
        # Initialize reporter
        self.reporter = None
        
    def run_server_process(self, server_file: str) -> subprocess.Popen:
        """Start MCP server process
        
        Args:
            server_file: MCP server file path
            
        Returns:
            Server process
        """
        # No longer need to manually start the process, langchain_mcp_adapters will handle it for us
        return None
        
    async def connect_to_mcp_server(self, server_file: str) -> bool:
        """Connect to MCP server
        
        Args:
            server_file: MCP server file path
            
        Returns:
            Whether connection was successful
        """
        try:
            # First disconnect any existing connections
            await self.disconnect_from_mcp_server()
            
            # Convert to absolute path
            abs_server_file = os.path.abspath(server_file)
            server_dir = os.path.dirname(abs_server_file)
            
            # Use StdioServerParameters to execute file directly instead of as module
            server_params = StdioServerParameters(
                command=sys.executable,  # Python interpreter
                args=[abs_server_file],  # Execute file directly instead of as module
                cwd=server_dir,  # Set working directory to server file directory
                env=os.environ.copy()
            )
            
            # Use tool manager to initialize connection and get tools, add 60-second timeout
            try:
                connection_task = self.tool_manager.initialize(server_params)
                self.tools = await asyncio.wait_for(connection_task, timeout=60.0)  # 60-second connection timeout
                return True
            except asyncio.TimeoutError:
                print(f"Warning: Connection to MCP server timed out (60 seconds)")
                # Ensure cleanup of resources
                await self.disconnect_from_mcp_server()
                return False
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Ensure cleanup of resources
            await self.disconnect_from_mcp_server()
            return False
            
    async def disconnect_from_mcp_server(self):
        """Disconnect from MCP server"""
        try:
            # Use tool manager to cleanup resources, add 10-second timeout
            cleanup_task = self.tool_manager.cleanup()
            await asyncio.wait_for(cleanup_task, timeout=10.0)  # 10-second cleanup timeout
        except asyncio.TimeoutError:
            print("Warning: MCP server disconnect timeout (10 seconds), forcing resource cleanup")
        except Exception as e:
            print(f"Error disconnecting from MCP server: {str(e)}")
        finally:
            # Always cleanup tool list regardless
            self.tools = []
    
    async def test_tool_async(self, tool_name: str, args: Dict) -> Tuple[Dict, float]:
        """Asynchronously test tool functionality
        
        Args:
            tool_name: Tool name
            args: Tool arguments
            
        Returns:
            (Response result, Response time)
        """
        start_time = time.time()
        result = None
        
        try:
            print(f"  Sending request: {tool_name} args: {json.dumps(args, ensure_ascii=False)[:100]}...")
                
            # Use tool manager to invoke tool, and set timeout
            result = await asyncio.wait_for(
                self.tool_manager.invoke_tool(tool_name, args),
                timeout=self.tool_timeout  # Use configured timeout time
            )
            
        except asyncio.TimeoutError:
            # Catch asyncio timeout error and throw our custom, more explicit exception
            raise ToolTimeoutError(f"Tool execution timed out after {self.tool_timeout} seconds.")
        except Exception as e:
            # For other types of exceptions, still return error dictionary
            result = {"error": str(e)}

        execution_time = time.time() - start_time
        
        # If result is string, convert to dictionary format
        if isinstance(result, str):
            result = {"result": result}
            
        return result, execution_time
     
    def get_test_files(self) -> List[str]:
        """Get test area file list
        
        Returns:
            Test area file path list
        """

        try:
            # Call file reading tool to list all files
            result = self.file_reader_tool._run(list_files=True)
            print(f"Found {len(result)} test area files")
            return result
        except Exception as e:
            print(f"Error getting test file list: {str(e)}")
            return []
            
    async def analyze_tool_and_generate_tests(self, tool: Dict, test_results: Dict = None) -> List[Dict]:
        """Analyze tool functionality and generate appropriate test cases
        
        Args:
            tool: Tool definition dictionary containing name and description
            test_results: Current execution results for memory function
        Returns:
            Test case list
        """
        # Parse response, extract JSON part
        import re
        import json
        # If no LLM, return empty list directly
        if self.llm is None:
            logger.error("LLM not available for test generation. Skipping.")
            return []
        
        # Get test area file list
        test_files = self.get_test_files()
        
        # Prepare tool description and parameter information
        tool_name = tool["name"]
        tool_description = tool["description"]
        tool_inputSchema = tool["args_schema"]
        
        # Analyze tool description to determine parameter structure
        has_arguments_wrapper = False
        if "arguments:" in tool_description.lower():
            has_arguments_wrapper = True
        
        # Build prompt, asking LLM to understand tool and generate test cases
        prompt_template = load_prompt("benchmark/generate_test_cases.prompt")
        
        arguments_wrapper_instruction = ""
        if has_arguments_wrapper:
            arguments_wrapper_instruction = "- If the tool description mentions that parameters are content contained in an arguments dictionary, use the arguments nested structure."
        
        no_arguments_wrapper_instruction = ""
        if not has_arguments_wrapper:
            no_arguments_wrapper_instruction = "- If the tool description directly lists parameter names and types, provide these parameters directly without nesting in arguments."
            
        arguments_example = ""
        if has_arguments_wrapper:
            arguments_example = '''
{
  "arguments": {
    "task": "Buy groceries"
  }
}
'''
        else:
            arguments_example = '''
{
  "topic": "artificial intelligence",
  "year_start": 2020,
  "limit": 5
}
'''
        prompt = prompt_template.format(
            tool_name=tool_name,
            tool_description=tool_description,
            tool_input_schema=tool_inputSchema,
            test_results_json=json.dumps(test_results, ensure_ascii=False, indent=2),
            test_files=test_files,
            arguments_wrapper_instruction=arguments_wrapper_instruction,
            no_arguments_wrapper_instruction=no_arguments_wrapper_instruction,
            arguments_example=arguments_example
        )
        try:
            if self.agent_logger:
                self.agent_logger.log(event_type="llm_test_generation_start", tool_name=tool_name)
                
            # Call LLM to generate test cases, add timeout control
            try:
                response = await asyncio.wait_for(
                    self.llm.ainvoke([HumanMessage(content=prompt)]), 
                    timeout=120.0
                )  # 120-second LLM call timeout
            except asyncio.TimeoutError:
                print(f"Warning: LLM call timeout (120 seconds) when generating test cases for tool '{tool_name}'")
                return []
            except Exception as e:
                print(f"LLM call error: {str(e)}")
                return []
            
            # Try to parse JSON directly
            test_cases = []
            try:
                test_cases = json.loads(response.content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON part
                json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
                if json_match:
                    test_cases_json = json_match.group(1)
                else:
                    # Try to match any content surrounded by []
                    json_match = re.search(r'\[(.*?)\]', response.content, re.DOTALL)
                    if json_match:
                        test_cases_json = f"[{json_match.group(1)}]"
                    else:
                        raise ValueError("Unable to extract JSON from LLM response")
                
                # Clean up JavaScript code that might cause JSON parsing errors
                test_cases_json = re.sub(r'\.repeat\(\d+\)', '""', test_cases_json)
                
                try:
                    test_cases = json.loads(test_cases_json)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    # Try to parse test cases one by one
                    test_cases = self.extract_valid_test_cases(test_cases_json)
            
            # No longer force parameter structure modification, let LLM decide parameter format based on tool description
            
            if self.agent_logger:
                self.agent_logger.log(event_type="llm_test_generated", 
                                      tool_name=tool_name, 
                                      test_count=len(test_cases))
            
            if not test_cases:
                logger.warning("Unable to parse any test cases from LLM response, will skip testing this tool.")
                return []
                
            return test_cases
            
        except Exception as e:
            logger.error(f"Error generating test cases: {e}", exc_info=True)
            if 'response' in locals():
                logger.error(f"LLM response: {response.content}")
            return []
            
    def extract_valid_test_cases(self, json_text: str) -> List[Dict]:
        """Extract valid test cases from JSON text that may contain errors
        
        Args:
            json_text: JSON text that may contain errors
            
        Returns:
            List of valid test cases
        """
        import re
        import json
        
        valid_cases = []
        
        # 1. Try to split and parse each test case
        # First remove all JavaScript expressions and comments
        cleaned_text = re.sub(r'\.repeat\(\d+\)', '""', json_text)
        cleaned_text = re.sub(r'//.*', '', cleaned_text)
        
        # Try to extract each independent JSON object
        try:
            # Find the start and end of each test case
            case_matches = []
            brace_count = 0
            start_idx = -1
            
            for i, char in enumerate(cleaned_text):
                if char == '{':
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        case_matches.append(cleaned_text[start_idx:i+1])
                        start_idx = -1
            
            # Parse each matched object
            for case_text in case_matches:
                try:
                    case = json.loads(case_text)
                    # Verify if it contains necessary fields
                    if "name" in case and "purpose" in case and "args" in case:
                        valid_cases.append(case)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"Error parsing test cases: {str(e)}")
            
        # 2. If the above method didn't find valid cases, try using regex
        if not valid_cases:
            try:
                # Use regex to match each test case
                case_pattern = re.compile(r'\{\s*"name":\s*"([^"]+)".*?"purpose":\s*"([^"]+)".*?"args":\s*(\{.*?\})\s*\}', re.DOTALL)
                
                for match in case_pattern.finditer(cleaned_text):
                    try:
                        name = match.group(1)
                        purpose = match.group(2)
                        args_text = match.group(3)
                        
                        # Try to parse args part
                        try:
                            args = json.loads(args_text)
                            valid_cases.append({
                                "name": name,
                                "purpose": purpose,
                                "args": args
                            })
                        except json.JSONDecodeError:
                            # If args parsing fails, use empty object
                            valid_cases.append({
                                "name": name,
                                "purpose": purpose,
                                "args": {}
                            })
                    except Exception:
                        continue
            except Exception as e:
                print(f"Error parsing test cases using regex: {str(e)}")
        
        # 3. If still no valid cases found, try to extract names and purposes, use empty parameters
        if not valid_cases:
            try:
                name_pattern = re.compile(r'"name":\s*"([^"]+)"')
                purpose_pattern = re.compile(r'"purpose":\s*"([^"]+)"')
                
                names = name_pattern.findall(cleaned_text)
                purposes = purpose_pattern.findall(cleaned_text)
                
                # Create basic test cases using found names and purposes
                for i in range(min(len(names), len(purposes))):
                    valid_cases.append({
                        "name": names[i],
                        "purpose": purposes[i],
                        "args": {}
                    })
            except Exception as e:
                print(f"Error extracting test case names and purposes: {str(e)}")
        
        print(f"Successfully extracted {len(valid_cases)} valid test cases")
        return valid_cases
    
    async def execute_test_suite_async(self, server_file: str, model_name: str) -> Dict:
        """Asynchronously execute complete test suite for a single MCP server
        
        Args:
            server_file: MCP server file path
            model_name: LLM model name to use
            
        Returns:
            Test result dictionary
        """
        suite_start_time = time.time()
        print(f"\n===== Starting server test: {os.path.basename(server_file)} =====")
        
        # Get server name, including parent directory name
        server_name = os.path.basename(server_file).replace('.py', '')
        parent_dir = os.path.basename(os.path.dirname(os.path.abspath(server_file)))
        
        # Optimize report name generation logic to handle complex naming from pipeline
        # project_name_override comes from <model_name>-<project_name> defined in main.py
        if self.project_name_override:
            report_name = self.project_name_override
        elif server_name == "server":
            report_name = f"{parent_dir}-{server_name}"
        else:
            report_name = server_name
        
        # Initialize LLM and logger using report_name
        agent_name = f"BenchmarkTester-Agent-{report_name}"
        if get_llm_for_agent:
            self.llm = get_llm_for_agent(agent_name, model_name)
            if self.llm is None:
                print(f"Warning: Unable to get LLM instance for '{model_name}', some advanced features may not be available")
        
        if get_agent_logger:
            self.agent_logger = get_agent_logger(agent_name)
            
        results = {
            "server_name": server_name,
            "parent_dir": parent_dir,
            "report_name": report_name,
            "server_path": server_file,
            "timestamp": datetime.now().isoformat(),
            "tools": [],
            "test_results": {},
            "total_cases": 0
        }
        
        # Connect to server
        server_connected = False
        try:
            # Connect to MCP server, add timeout control
            print("\nConnecting to MCP server...")
            try:
                connection_task = self.connect_to_mcp_server(server_file)
                server_connected = await asyncio.wait_for(connection_task, timeout=120.0)  # 2-minute connection timeout
                if not server_connected:
                    raise RuntimeError("Unable to connect to MCP server")
            except asyncio.TimeoutError:
                raise RuntimeError("Connection to MCP server timed out (120 seconds)")
            
            # Get tool list
            if not hasattr(self, 'tools') or not self.tools:
                raise RuntimeError("Failed to get MCP server tool list")
            
            for tool in self.tools:
                # Add tool information to results, keeping only name and description
                tool_info = {
                    "name": tool.name,
                    "description": getattr(tool, "description", ""),
                    "args_schema": getattr(tool, "args_schema", {})
                }
                results["tools"].append(tool_info)

            # Set overall test timeout protection (30 minutes)
            test_phase_timeout = 30 * 60  # seconds
            test_phase_start = time.time()

            order_start_time = time.time()
            # You need to complete letting LLM decide tool order, then execute tests in order
            prompt_template = load_prompt("benchmark/decide_tool_order.prompt")
            prompt = prompt_template.format(
                tools_json=json.dumps(results["tools"], ensure_ascii=False, indent=2)
            )
            
            try:
                # Add LLM call timeout
                response = await asyncio.wait_for(
                    self.llm.ainvoke([HumanMessage(content=prompt)]),
                    timeout=60.0
                ) # 60-second LLM call timeout
                content = response.content
            except asyncio.TimeoutError:
                print("Warning: LLM tool order decision timeout (60 seconds), will use default order")
                content = "[]"  # Use empty list, will fall back to default order later
            except Exception as e:
                print(f"LLM tool order decision error: {str(e)}, will use default order")
                content = "[]"  # Use empty list, will fall back to default order later
                
            default_tool_order = [t["name"] for t in results["tools"]]
            tool_order = default_tool_order  # Default to using the order of tools as retrieved

            try:
                # Try to extract JSON from Markdown code block
                match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
                if match:
                    json_str = match.group(1).strip()
                    parsed_order = json.loads(json_str)
                else:
                    # If no code block, try to parse the entire returned content directly
                    parsed_order = json.loads(content)

                # Verify if the returned tool list is valid (contains all expected tools)
                if isinstance(parsed_order, list) and set(parsed_order) == set(default_tool_order):
                    tool_order = parsed_order
                    print("LLM successfully determined tool test order.")
                else:
                    print("LLM returned invalid tool list (tools don't match), will use default order.")
            except json.JSONDecodeError:
                print("LLM returned content is not valid JSON format, will use default order.")

            order_end_time = time.time()
            if self.agent_logger:
                self.agent_logger.log(event_type="llm_test_order_generated", 
                                      tool_test_order=tool_order,
                                      order_generate_time=order_end_time - order_start_time)
            # Test metrics recording
            total_count = 0
            total_response_time = 0

            # Implement the logic of "generate test cases then execute, then generate more cases based on execution results, then execute again"
            # Initialize test_results
            results["test_results"] = {}
            
            # Flag for detecting consecutive timeouts
            last_tool_timed_out = False
            
            # Process each tool in order
            for tool_name in tool_order:
                # Check if overall test has timed out
                if time.time() - test_phase_start > test_phase_timeout:
                    print(f"Warning: Overall test phase has timed out ({test_phase_timeout} seconds), aborting remaining tests")
                    results["abnormal_termination"] = f"Test phase timeout after {test_phase_timeout} seconds"
                    break
                    
                tool = next((t for t in results["tools"] if t["name"] == tool_name), None)
                if not tool:
                    continue
                    
                tool_generate_start_time = time.time()
                    
                print(f"\nGenerating test cases for tool '{tool_name}'...")
                
                
                # To save tokens, only pass test results from the first two tools as context
                limited_test_results = {}
                # Get names of the first two tools in the predetermined order
                context_tool_names = tool_order[:2]
                # Filter out results of these two tools from already executed test results
                for ctx_tool_name in context_tool_names:
                    if ctx_tool_name in results["test_results"]:
                        limited_test_results[ctx_tool_name] = results["test_results"][ctx_tool_name]

                # Call LLM to generate test cases, add timeout control
                try:
                    generate_task = self.analyze_tool_and_generate_tests(tool, limited_test_results)
                    cases = await asyncio.wait_for(generate_task, timeout=600.0)  # 10-minute generation timeout
                    print(f"  Generated {len(cases)} test cases")
                except asyncio.TimeoutError:
                    print(f"  Warning: Test case generation timeout (10 minutes) for tool '{tool_name}', skipping this tool")
                    continue
                except Exception as e:
                    print(f"  Error generating test cases for tool '{tool_name}': {str(e)}, skipping this tool")
                    continue
                    
                tool_generate_time = time.time() - tool_generate_start_time
                if self.agent_logger:
                    self.agent_logger.log(event_type="llm_test_case_generated", 
                                          tool_name=tool_name,
                                          case_generate_time=tool_generate_time,
                                          test_cases_count=len(cases))

                
                # Initialize current tool's test result list
                results["test_results"][tool_name] = []
                
                current_tool_had_timeout = False
                consecutive_timeouts_count = 0  # Add consecutive timeout counter
                max_consecutive_timeouts = self.max_consecutive_timeouts  # Use configured timeout count
                
                tool_all_cases_start_time = time.time()
                # Immediately execute all test cases for this tool
                for case in cases:
                    # Check if overall test has timed out
                    if time.time() - test_phase_start > test_phase_timeout:
                        print(f"Warning: Overall test phase has timed out ({test_phase_timeout} seconds), aborting remaining tests")
                        results["abnormal_termination"] = f"Test phase timeout after {test_phase_timeout} seconds"
                        break
                        
                    case_execute_start_time = time.time()
                    case_name = case["name"]
                    case_args = case["args"]
                    is_functional_test = case.get("is_functional_test", False)
                    
                    print(f"  Executing test: {case_name}")
                    
                    response, exec_time = None, 0.0
                    is_timeout = False
                    
                    try:
                        # Execute single test case, timeout here should be slightly longer than internal timeout as a safeguard
                        response, exec_time = await asyncio.wait_for(
                            self.test_tool_async(tool_name, case_args),
                            timeout=self.tool_timeout + 10.0
                        )
                    except ToolTimeoutError as e:
                        # Catch our custom timeout exception
                        print(f"    Warning: Test case '{case_name}' execution timed out.")
                        is_timeout = True
                        response = {"error": str(e)}
                        exec_time = self.tool_timeout # Use preset timeout time as execution time
                    except asyncio.TimeoutError:
                        # Catch hard timeout (if test_tool_async itself hangs)
                        print(f"    Warning: Test case '{case_name}' execution hard timeout ({self.tool_timeout + 10} seconds)")
                        is_timeout = True
                        response = {"error": f"Test case execution hard-timed out after {self.tool_timeout + 10.0} seconds"}
                        exec_time = self.tool_timeout + 10.0
                    except Exception as e:
                        print(f"    Test case '{case_name}' execution error: {str(e)}")
                        response = {"error": str(e)}
                        exec_time = time.time() - case_execute_start_time


                    if self.agent_logger:
                        self.agent_logger.log(event_type="llm_test_case_executed", 
                                              tool_name=tool_name,
                                              case_name=case_name,
                                              case_args=case_args,
                                              response=response,
                                              execution_time=exec_time)
                    
                    # Check if timeout occurred, handle all timeout situations uniformly
                    if is_timeout:
                        current_tool_had_timeout = True
                        consecutive_timeouts_count += 1
                        print(f"    Warning: Test case '{case_name}' execution timeout ({consecutive_timeouts_count}/{max_consecutive_timeouts})")
                        
                        # If consecutive timeout count reaches threshold, skip remaining test cases for this tool
                        if consecutive_timeouts_count >= max_consecutive_timeouts:
                            print(f"    Warning: {max_consecutive_timeouts} consecutive test cases timed out, skipping remaining test cases for tool '{tool_name}'")
                            break
                    else:
                        # Any success resets the counter
                        consecutive_timeouts_count = 0
                    
                    total_count += 1
                    total_response_time += exec_time
                    
                    # Add test result to current tool's result list
                    results["test_results"][tool_name].append({
                        "case_name": case_name,
                        "purpose": case.get("purpose", ""),
                        "args": case_args,
                        "response": response,
                        "execution_time": exec_time,
                        "is_functional_test": is_functional_test
                    })
                    
                    print(f"    Execution time: {exec_time:.2f}s")
                
                # Record tool total execution time
                tool_execute_time = time.time() - tool_all_cases_start_time
                if self.agent_logger:
                    self.agent_logger.log(
                        event_type="tool_execution_summary",
                        tool_name=tool_name,
                        tool_all_case_execute_time=tool_execute_time,
                        test_cases_count=len(cases),
                        timeout_cases_count=consecutive_timeouts_count if current_tool_had_timeout else 0
                    )

                # Check for consecutive timeouts
                if last_tool_timed_out and current_tool_had_timeout:
                    print(f"Warning: Tool '{tool_name}' timed out, and the previous tool also timed out. Aborting test.")
                    results["abnormal_termination"] = "Consecutive tool timeouts indicate a server issue."
                    break  # Break tool loop
                
                last_tool_timed_out = current_tool_had_timeout

            # Update total test case count
            results["total_cases"] = total_count
            
            # Save results
            self.benchmark_results[report_name] = results
            
            # Initialize reporter and pass LLM and logger
            self.reporter = Reporter(
                output_dir=self.output_dir, 
                llm=self.llm, 
                agent_logger=self.agent_logger,
                file_reader_tool=self.file_reader_tool
            )
            
            # Use Reporter to generate reports
            self.reporter.save_test_report(results)
            if self.llm:
                await self.reporter.generate_detailed_report(results)
            self.reporter.visualize_results(report_name, results)
            
            # Calculate and record total execution time
            suite_duration = time.time() - suite_start_time
            if self.agent_logger:
                # Statistics LLM usage
                total_tokens, total_cost = self.agent_logger.get_llm_usage_summary()
                self.agent_logger.log(
                    event_type="test_suite_summary",
                    report_name=report_name,
                    duration=suite_duration,
                    total_llm_tokens=total_tokens,
                    total_cost=total_cost
                )

        except Exception as e:
            print(f"Test error: {str(e)}")
            import traceback
            traceback.print_exc()
            results["error"] = str(e)
            
        finally:
            # Disconnect from server to ensure it doesn't hang
            if server_connected:
                try:
                    disconnect_task = self.disconnect_from_mcp_server()
                    await asyncio.wait_for(disconnect_task, timeout=20.0)  # 20-second disconnect timeout
                except asyncio.TimeoutError:
                    print("Warning: MCP server disconnect timeout (20 seconds), forcing continuation")
                except Exception as e:
                    print(f"Error disconnecting from server: {str(e)}")
        
        print(f"\n===== Server {server_name} test completed =====")
        
        # Add suite summary information to main result dictionary
        suite_duration = time.time() - suite_start_time
        total_tokens, total_cost = (0, 0)
        if self.agent_logger:
            total_tokens, total_cost = self.agent_logger.get_llm_usage_summary()

        results["suite_summary"] = {
            "total_duration": suite_duration,
            "total_llm_tokens": total_tokens,
            "total_cost": total_cost,
        }
        
        return results

    def execute_test_suite(self, server_file: str, model_name: str = "qwen-plus") -> Dict:
        """Execute complete test suite for a single MCP server
        
        Args:
            server_file: MCP server file path
            model_name: LLM model name to use
            
        Returns:
            Test result dictionary
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.execute_test_suite_async(server_file, model_name))
    

    
    async def generate_detailed_report(self, results: Dict) -> str:
        """This method has been moved to Reporter class"""
        if self.reporter:
            return await self.reporter.generate_detailed_report(results)
        return None
    
    def visualize_results(self, report_name: str, results: Dict) -> None:
        """This method has been moved to Reporter class"""
        if self.reporter:
            self.reporter.visualize_results(report_name, results)

    def save_test_report(self, results: Dict) -> None:
        """This method has been moved to Reporter class"""
        if self.reporter:
            self.reporter.save_test_report(results)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="MCP Server Intelligent Testing Tool")
    
    parser.add_argument(
        "server_file",
        nargs="?",
        help="Path to the MCP server file to test"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./server-test-report",
        help="Test report output directory"
    )
    
    parser.add_argument(
        "--model-name",
        default="qwen-plus",
        help="LLM model name to use for testing"
    )
    
    parser.add_argument(
        "--test-files-dir",
        help="Test files directory path for providing test data"
    )
    
    parser.add_argument(
        "--tool-timeout",
        type=float,
        default=40.0,
        help="Tool execution timeout (seconds), default 40 seconds"
    )
    
    parser.add_argument(
        "--max-consecutive-timeouts",
        type=int,
        default=3,
        help="Maximum consecutive timeout count, default 3"
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    
    # Check if server file exists
    server_file = args.server_file
    if server_file and not os.path.exists(server_file):
        print(f"Error: Server file '{server_file}' does not exist")
        return 1
        
    # Create tester and test server
    tester = MCPIntelligentTester(
        output_dir=args.output_dir, 
        test_files_dir=args.test_files_dir,
        tool_timeout=args.tool_timeout,
        max_consecutive_timeouts=args.max_consecutive_timeouts
    )
    
    if server_file:
        results = tester.execute_test_suite(server_file, model_name=args.model_name)
        
        # Get report name
        report_name = results.get("report_name", results.get("server_name", "Unknown Server"))
        
        # Display scores
        print("\n====== Test Scores ======")
        print(f"Report Name: {report_name}")
        print(f"Total Score: {results.get('total_score', 0)}/100 points")
        
        for dimension in SCORE_DIMENSIONS:
            dimension_score = results.get("scores", {}).get(dimension, 0)
            print(f"{dimension}: {dimension_score}/{SCORE_WEIGHTS[dimension]} points")
        
        print(f"\nTest report has been saved to {args.output_dir} directory")
    else:
        print("No server file path provided, please specify the MCP server file to test")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 