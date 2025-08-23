import json
import asyncio
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any
import re

from langchain_core.messages import HumanMessage
from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.mcp_swe_flow.config import PROJECT_ROOT, get_llm_for_agent
from framwork.tool import save_file_tool
from framwork.mcp_swe_flow.adapters import MCPClientAdapter
from framwork.logger import logger, get_agent_logger
from framwork.mcp_swe_flow.prompts.utils import load_prompt

def _substitute_parameters(params: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively substitutes placeholders in a parameter dictionary.
    This version uses a robust greedy traversal logic to handle keys containing dots.
    Placeholder format: "$outputs.step_id.json_path" or "$outputs.step_id[index].json_path"
    """
    substituted_params = {}
    for key, value in params.items():
        if isinstance(value, str) and value.startswith("$outputs."):
            try:
                placeholder = value.replace("$outputs.", "")
                
                # Extract step_id using regex, stopping at the first '[' or '.'
                match = re.match(r'^([a-zA-Z0-9_]+)', placeholder)
                if not match:
                    raise ValueError(f"Invalid placeholder format: could not extract step_id from '{placeholder}'")
                
                step_id = match.group(1)
                path_to_process = placeholder[len(step_id):]
                
                if step_id not in outputs:
                    raise KeyError(f"Step ID '{step_id}' not found in outputs")

                current_value = outputs[step_id]['result']
                
                # --- Robust JSON parsing ---
                if isinstance(current_value, str):
                    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', current_value, re.DOTALL)
                    str_to_parse = json_match.group(1).strip() if json_match else current_value
                    try:
                        current_value = json.loads(str_to_parse)
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse output from step '{step_id}' as JSON. Proceeding with raw string.")
                
                # --- Greedy Traversal Logic ---
                while path_to_process:
                    # Check for index access first
                    match_index = re.match(r'\[(\d+)\]', path_to_process)
                    if match_index:
                        index = int(match_index.group(1))
                        if not isinstance(current_value, list):
                            raise TypeError(f"Cannot apply index [{index}] to non-list value (type: {type(current_value).__name__}).")
                        current_value = current_value[index]
                        path_to_process = path_to_process[match_index.end():]
                        continue

                    # If not an index, it must be a dot-prefixed key
                    if not path_to_process.startswith('.'):
                        raise ValueError(f"Invalid path segment in placeholder: '{path_to_process}'")
                    
                    path_to_process = path_to_process[1:] # Consume the dot
                    
                    # Find the end of the current key segment (before next '[' or end of string)
                    key_segment_match = re.match(r'[^\[\]]+', path_to_process)
                    key_segment = key_segment_match.group(0)
                    
                    # Process this segment using greedy key matching
                    sub_keys_to_process = key_segment.split('.')
                    while sub_keys_to_process:
                        matched = False
                        # Try to match the longest possible key from the remaining parts
                        for i in range(len(sub_keys_to_process), 0, -1):
                            potential_key = ".".join(sub_keys_to_process[0:i])
                            if isinstance(current_value, dict) and potential_key in current_value:
                                current_value = current_value[potential_key]
                                # Consume the matched parts
                                sub_keys_to_process = sub_keys_to_process[i:]
                                matched = True
                                break # Restart the while loop with remaining sub_keys
                        
                        if not matched:
                            unresolved_key = ".".join(sub_keys_to_process)
                            raise KeyError(f"Could not resolve key '{unresolved_key}' in placeholder '{value}'")
                    
                    # Consume the processed segment from the main path
                    path_to_process = path_to_process[len(key_segment):]

                substituted_params[key] = current_value

            except (KeyError, TypeError, IndexError, ValueError) as e:
                logger.error(f"❌ Failed to resolve placeholder '{value}': {e}")
                substituted_params[key] = None # Mark as failed
        elif isinstance(value, dict):
            substituted_params[key] = _substitute_parameters(value, outputs)
        elif isinstance(value, list):
            substituted_params[key] = [
                _substitute_parameters(item, outputs) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            substituted_params[key] = value
    return substituted_params

def _validate_test_plan(test_plan: List[Dict[str, Any]]):
    """Validates the structure and logic of the test plan."""
    defined_step_ids = set()
    for i, step in enumerate(test_plan):
        if not all(k in step for k in ["step_id", "tool_name", "parameters", "description"]):
            raise ValueError(f"Test plan step {i+1} is missing required fields ('step_id', 'tool_name', 'parameters', 'description').")
        
        step_id = step["step_id"]
        if step_id in defined_step_ids:
            raise ValueError(f"Found duplicate step_id in test plan: '{step_id}'")
        
        params_str = json.dumps(step["parameters"])
        dependencies = re.findall(r'"\$outputs\.([^.\["]+)', params_str)
        for dep_id in dependencies:
            if dep_id not in defined_step_ids:
                raise ValueError(f"Step '{step_id}' depends on an undefined step '{dep_id}'.")
        
        defined_step_ids.add(step_id)
    logger.info("✅ Test plan validation passed.")


async def _execute_test_plan(mcp_adapter: MCPClientAdapter, test_plan: List[Dict[str, Any]], agent_logger) -> List[Dict[str, Any]]:
    """
    Executes the test plan, handling dependencies and logging results.
    This function does not interact with an LLM.
    """
    logger.info("🚀 Starting test plan execution...")
    execution_log = []
    step_outputs = {}

    for i, step in enumerate(test_plan):
        step_id = step.get("step_id")
        tool_name = step.get("tool_name")
        params = step.get("parameters", {})
        description = step.get("description", "No description")

        logger.info(f"🔄 (Step {i+1}/{len(test_plan)}) Preparing to execute: {step_id} - {tool_name}")
        agent_logger.log(event_type="test_step_start", step_id=step_id, tool_name=tool_name, description=description)

        substituted_params = _substitute_parameters(params, step_outputs)
        
        try:
            # Propagate failure: if any substituted parameter is None due to a previous step's failure, this step should also fail.
            if any(v is None for v in substituted_params.values()):
                # Find the first placeholder that resolved to None
                failed_placeholder = next((p_val for p_key, p_val in params.items() if substituted_params.get(p_key) is None), "unknown")
                raise ValueError(f"A required parameter resolved to None, likely due to a failure in a dependency. Failed placeholder: '{failed_placeholder}'")

            tool_to_invoke = next((t for t in mcp_adapter.tools if t.name == tool_name), None)
            if not tool_to_invoke:
                raise ValueError(f"Tool '{tool_name}' not found in adapter")

            # Enhanced robustness: add a 60-second timeout for the tool call
            result = await asyncio.wait_for(
                tool_to_invoke.ainvoke(substituted_params),
                timeout=60.0
            )

            # 检查结果是否包含错误信息，但排除适配器截断标记
            is_error_in_result = isinstance(result, str) and (
                ("error" in result.lower() 
                or "failed" in result.lower() 
                or "invalid" in result.lower()
                or "exception" in result.lower())
                # 排除适配器截断标记导致的误判
                and not ("adapter_truncation_note" in result.lower() or "__adapter_truncation_note__" in result.lower())
            )

            if is_error_in_result:
                logger.warning(f"    - ⚠️  Tool '{tool_name}' returned a potential error message: {result}")
                step_result = {"status": "error", "result": result}
                agent_logger.log(event_type="test_step_error", step_id=step_id, error=f"Tool returned an error message: {result}")
            else:
                # 检查是否存在适配器截断标记
                has_adapter_truncation = isinstance(result, str) and ("adapter_truncation_note" in result.lower() or "__adapter_truncation_note__" in result.lower())
                if has_adapter_truncation:
                    logger.info(f"    - ℹ️ Execution successful with adapter truncation (not a tool error): {result[:200]}...")
                else:
                    logger.info(f"    - ✅ Execution successful: {result}")
                    
                step_result = {"status": "success", "result": result}
                agent_logger.log(event_type="test_step_success", step_id=step_id, result=result)
        
        except asyncio.TimeoutError:
            error_msg = f"Tool '{tool_name}' execution timed out (exceeded 60 seconds)."
            logger.error(f"    - ❌ {error_msg}")
            step_result = {"status": "error", "result": error_msg}
            agent_logger.log(event_type="test_step_timeout", step_id=step_id, error=error_msg)

        except Exception as e:
            error_msg = f"Tool '{tool_name}' call failed: {e}"
            logger.error(f"    - ❌ {error_msg}")
            step_result = {"status": "error", "result": str(e)}
            agent_logger.log(event_type="test_step_error", step_id=step_id, error=str(e))
        
        step_outputs[step_id] = step_result
        execution_log.append({
            "step": step,
            "substituted_params": substituted_params,
            "result": step_result
        })

    logger.info("✅ Test plan execution completed.")
    return execution_log


async def server_test_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """
    Server test node, using a "Plan-Execute-Report" three-stage model.
    """
    api_name = state.get("api_name")
    agent_logger = get_agent_logger(f"ServerTest-Agent-{api_name or 'custom'}")

    # Add the logger's file path to the state for aggregation later
    log_files = state.get("log_files", [])
    if agent_logger.log_path and str(agent_logger.log_path) not in log_files:
        log_files.append(str(agent_logger.log_path))

    agent_logger.log(event_type="start_node", state=state)
    logger.info("--- Starting Server Test Node (Three-Stage Model) ---")
    
    update = {}
    mcp_adapter = MCPClientAdapter()    
    
    try:
        server_file_path_str = state.get("server_file_path")
        project_dir_str = state.get("project_dir")
        
        if not server_file_path_str or not project_dir_str:
            raise ValueError("Missing 'server_file_path' or 'project_dir' in state.")

        server_file_path = Path(server_file_path_str)
        project_dir = Path(project_dir_str)
        current_test_output_dir = server_file_path.parent
        
        if not server_file_path.exists():
            raise FileNotFoundError(f"Server file not found: {server_file_path}")

        server_code = server_file_path.read_text(encoding='utf-8')
        update["server_code"] = server_code
        logger.info(f"✅ Successfully read server code: {server_file_path}")

        # 根据路径特征选择合适的连接方式
        if "gemini-2.5-pro" in str(server_file_path):
            logger.info(f"🔍 检测到 Gemini 模型生成的服务器，使用文件路径方式连接")
            logger.info(f"🚀 Starting and connecting to MCP server file: {server_file_path}")
            await mcp_adapter.connect_stdio_file(str(server_file_path), cwd=PROJECT_ROOT)
            agent_logger.log(event_type="mcp_adapter_connected", connection_type="file", file_path=str(server_file_path))
        else:
            # 原有的模块导入方式
            relative_path = server_file_path.relative_to(PROJECT_ROOT) 
            module_name = str(relative_path).replace(".py", "").replace(os.path.sep, ".")
            
            logger.info(f"🚀 Starting and connecting to MCP server module: {module_name}")
            await mcp_adapter.connect_stdio(module_name, cwd=PROJECT_ROOT)
            agent_logger.log(event_type="mcp_adapter_connected", connection_type="module", module_name=module_name)
        
        # ----------------- Stage 1: Generate Test Plan -----------------
        logger.info("=============== Stage 1: Generate Test Plan ===============")
        
        tools_info = [{
            "name": tool.name,
            "description": tool.description,
            "args_schema": tool.args_schema
        } for tool in mcp_adapter.tools]
        
        # New: List available files in the test files directory
        test_files_dir = PROJECT_ROOT / "testSystem" / "testFiles"
        test_files_info = "No test files currently available."
        if test_files_dir.exists() and test_files_dir.is_dir():
            try:
                test_files_paths = [str(f.resolve()) for f in test_files_dir.iterdir() if f.is_file()]
                if test_files_paths:
                    test_files_info = (
                        "The following files are available for testing. When testing tools that require file paths,"
                        "you **must** use the absolute paths provided below:\n"
                        + "\n".join([f"- `{path}`" for path in test_files_paths])
                    )
                logger.info(f"Found test files:\n{test_files_info}")
            except Exception as e:
                logger.warning(f"Error scanning test file directory '{test_files_dir}': {e}")
                test_files_info = f"Error scanning for test files: {e}"
        else:
            logger.warning(f"Test file directory not found: {test_files_dir}")

        plan_template = load_prompt("server_tester/generate_test_plan.prompt")
        plan_prompt = plan_template.render(
            tool_schemas=json.dumps(tools_info, indent=2, ensure_ascii=False),
            server_code=server_code,
            test_files_info=test_files_info
        )
        
        logger.info("🤖 Requesting LLM to generate test plan...")
        test_agent_llm = get_llm_for_agent(f"ServerTest-Agent-{api_name}")
        plan_response = await test_agent_llm.ainvoke([HumanMessage(content=plan_prompt)])
        
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', plan_response.content)
        json_str = json_match.group(1).strip() if json_match else plan_response.content
        test_plan = json.loads(json_str).get("test_plan", [])

        if not test_plan:
            raise ValueError("Generated test plan is empty or incorrectly formatted.")
        logger.info(f"✅ Successfully parsed test plan with {len(test_plan)} steps.")
        logger.info(f"✅ Successfully parsed test plan:{test_plan}")
        
        # Enhanced robustness: validate the test plan
        _validate_test_plan(test_plan)

        # ----------------- Stage 2: Execute Test Plan -----------------
        logger.info("=============== Stage 2: Execute Test Plan ===============")
        execution_log = await _execute_test_plan(mcp_adapter, test_plan, agent_logger)
        
        # Enhanced robustness: persist the raw execution log
        try:
            workspace_dir = PROJECT_ROOT / "workspace"
            log_file_name = f"execution_log_{api_name or 'custom'}.json"
            
            # Corrected path calculation: relative to the 'workspace' directory, and using the current test's output directory
            relative_log_path = current_test_output_dir.relative_to(workspace_dir) / log_file_name
            
            await save_file_tool.ainvoke({
                "file_path": str(relative_log_path), 
                "content": json.dumps(execution_log, indent=2, ensure_ascii=False)
            })
            log_path = current_test_output_dir / log_file_name # For logging the absolute path
            logger.info(f"💾 Raw execution log saved to: {log_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save raw execution log: {e}")

        # ----------------- Stage 3: Generate Final Report -----------------
        logger.info("=============== Stage 3: Generate Final Report ===============")
        report_context = {
            "server_code": server_code,
            "tool_schemas_json": json.dumps(tools_info, indent=2, ensure_ascii=False),
            "execution_log_json": json.dumps(execution_log, indent=2, ensure_ascii=False),
            "api_name": api_name,
            "api_spec_json": json.dumps(state.get("api_spec"), indent=2, ensure_ascii=False) if state.get("api_spec") else "{}",
            "user_input": state.get("user_input", "")
        }
        report_prompt = load_prompt("server_tester/final_report.prompt").render(**report_context)
        
        logger.info("🤖 Requesting LLM to generate final test report...")
        report_response = await test_agent_llm.ainvoke([HumanMessage(content=report_prompt)])
        test_report_content = report_response.content
        logger.info("✅ Successfully generated test report.")

        # Save report
        report_file_name = f"test_report_{api_name or 'custom'}.md"
        
        # Corrected path calculation: relative to the 'workspace' directory, and using the current test's output directory
        workspace_dir = PROJECT_ROOT / "workspace"
        relative_report_path = current_test_output_dir.relative_to(workspace_dir) / report_file_name
        
        await save_file_tool.ainvoke({"file_path": str(relative_report_path), "content": test_report_content})
        report_path = current_test_output_dir / report_file_name # For logging the absolute path
        logger.info(f"✅ Test report saved to: {report_path}")
        
        update["test_report_path"] = str(report_path)
        update["test_report_content"] = test_report_content
        update["next_step"] = "refine_code"

        # Ensure critical state is passed to the next node to prevent loss
        update['server_file_path'] = state.get('server_file_path')
        update['mcp_doc'] = state.get('mcp_doc')
        update['project_dir'] = str(project_dir) # Pass the stable project root directory
        # Explicitly carry over the refinement loop count to ensure it's not lost
        if "refinement_loop_count" in state:
            update["refinement_loop_count"] = state.get("refinement_loop_count")
        
    except Exception as e:
        error_details = traceback.format_exc()
        # Standardize error message format to ensure the error handler can recognize and route to the recovery node
        error_message = f"Server test failed: {e}"
        logger.error(f"❌ A critical error occurred in the test node: {error_message}\n{error_details}")
        agent_logger.log(event_type="error", error=str(e), details=error_details)
        update.update({
            "error": error_message, 
            "next_step": "error_handler",
            "error_source": "server_test"
        })
    
    finally:
        if mcp_adapter and mcp_adapter.session:
            await mcp_adapter.disconnect()
            logger.info("✅ Server process has been terminated.")
            agent_logger.log(event_type="server_shutdown")
            
        # Give the event loop a moment to clean up before exiting
        await asyncio.sleep(0.1)
            
        agent_logger.log(event_type="end_node", update=update)
        logger.info("--- ✅ Server Test Node Completed ---")
        update["log_files"] = log_files # Ensure log_files list is in the final update
        return {**state, **update} 