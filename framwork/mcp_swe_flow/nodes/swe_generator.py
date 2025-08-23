import json
from pathlib import Path
import re
import asyncio
import os

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.mcp_swe_flow.config import get_llm_for_agent, llm, get_env_int
from framwork.tool import tavily_search_tool, save_file_tool, context7_docs_tool
from framwork.logger import logger, get_agent_logger
from framwork.mcp_swe_flow.prompts.utils import load_prompt


def _normalize_and_extract_tool_calls(response_message: AIMessage) -> AIMessage:
    """
    Normalizes tool calls that might be misplaced in additional_kwargs or have a non-standard structure.
    This is a defensive measure for models that don't adhere to the standard
    tool_calls attribute format, especially when the main content is empty.
    """
    raw_tool_calls = response_message.tool_calls or response_message.additional_kwargs.get("tool_calls", [])
    if not raw_tool_calls:
        return response_message

    logger.info("Normalizing tool call structure...")
    logger.info("Raw tool calls: {}", raw_tool_calls)  # Use placeholder for safety

    normalized_calls = []
    for call in raw_tool_calls:
        try:
            if "function" in call and isinstance(call.get("function"), dict):
                # Handles nested structure: {'id': '...', 'function': {'name': '...', 'arguments': '...'}}
                function_data = call.get("function", {})
                name = function_data.get("name")
                args_str = function_data.get("arguments", "{}")

                # Defensive parsing of arguments
                try:
                    # The "happy path": arguments is a valid JSON string.
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    # The "brute-force" fallback: arguments is not valid JSON,
                    # but likely contains the code content we need.
                    logger.warning("JSON parsing failed for tool arguments. Attempting regex-based content extraction.")
                    match = re.search(r'^{\s*"content"\s*:\s*"(.*)"\s*}$', args_str, re.DOTALL)
                    if match:
                        content = match.group(1).replace('\\"', '"').replace("\\'", "'")
                        args = {'content': content}
                        logger.info("Successfully extracted code content using regex fallback.")
                    else:
                        logger.error("Regex fallback also failed to extract code from arguments.")
                        args = {"_raw_arguments": args_str}

                normalized_calls.append({
                    "name": name,
                    "args": args,
                    "id": call.get("id"),
                    "type": "tool_call"  # Ensure type is added
                })
            elif "name" in call and "args" in call:
                # Handles standard structure
                call.setdefault("type", "tool_call")  # Ensure type exists
                normalized_calls.append(call)
            else:
                logger.warning("Skipping malformed tool call with unknown structure: {}", call)  # Use placeholder
        except Exception as e:
            logger.error("Error processing a tool call: {}. Error: {}", call, e, exc_info=True)  # Use placeholder

    # Replace the original tool_calls with the fully normalized list
    response_message.tool_calls = normalized_calls
    
    # Clean up additional_kwargs to prevent downstream confusion
    if "tool_calls" in response_message.additional_kwargs:
        del response_message.additional_kwargs["tool_calls"]
        
    return response_message


async def swe_generate_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """Asynchronously generates MCP server code using LLM and saves it using a tool."""
    api_name = state.get("api_name")
    api_spec = state.get("api_spec")
    mcp_doc = state.get("mcp_doc")
    user_input = state.get("user_input")
    # Get the specified model for the SWE agent, providing a fallback to prevent None.
    swe_model = state.get("swe_model") or os.getenv("SWE_AGENT_MODEL")

    if not api_name and user_input:
        api_name = await generate_server_name_from_user_input(user_input, swe_model)
    
    if not api_name:
        api_name = "unnamed_mcp_server"

    # Create a dedicated project directory for all outputs, structured by model name
    workspace_dir = Path("workspace")
    output_servers_dir = workspace_dir / "pipeline-output-servers"
    # New directory structure: /pipeline-output-servers/<model_name>/<api_name>
    project_dir = output_servers_dir / swe_model / api_name
    
    # Ensure all directories in the path are packages
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files to make directories importable packages
    # This needs to be done for all parent directories up to the workspace root for the tool
    p = project_dir
    while p != workspace_dir:
        (p / "__init__.py").touch(exist_ok=True)
        p = p.parent

    # The path for the tool is relative to the tool's workspace_root ("workspace/")
    tool_relative_project_dir = project_dir.relative_to(workspace_dir)
    server_file_name = f"{api_name}.py"
    relative_save_path = tool_relative_project_dir / server_file_name
    # The absolute path will be stored in the workflow state for subsequent nodes
    absolute_server_path = (project_dir / server_file_name).resolve()

    agent_logger = get_agent_logger(f"SWE-Agent-{api_name}")
    
    # Add the logger's file path to the state for aggregation later
    log_files = state.get("log_files", [])
    if agent_logger.log_path and agent_logger.log_path not in log_files:
        log_files.append(str(agent_logger.log_path))

    logger.info("--- Starting SWE Generate Node ---")
    agent_logger.log(event_type="start_node", state=state)
    
    base_llm = get_llm_for_agent(f"SWE-Agent-{api_name}", model_override=swe_model) 
    if base_llm is None:
         logger.error("LLM is not initialized. Cannot proceed.")
         return {**state, "error": "LLM not initialized", "next_step": "error_handler"}

    if not mcp_doc:
        logger.error("Missing required MCP documentation.")
        return {**state, "error": "Missing required MCP documentation.", "next_step": "error_handler"}

    # --- Phase 1: Planning ---
    logger.info("--- Starting SWE Planning Phase ---")
    agent_logger.log(event_type="start_planning_phase")

    planning_tools = [tavily_search_tool]
    planning_llm = base_llm.bind_tools(planning_tools)
    logger.info(f"SWE-Planner has been equipped with tools: {[tool.name for tool in planning_tools]}")

    is_api_mode = api_spec is not None and api_name is not None
    if is_api_mode:
        request_specific_part = f"""
OpenAPI Specification:
```json
{json.dumps(api_spec, indent=2, ensure_ascii=False)}
```
"""
    else:
        request_specific_part = f"""
User Request:
{user_input}
"""

    MAX_PLANNING_TURNS = get_env_int("MAX_PLANNING_TURNS", 4)
    MAX_PLANNING_TOOL_CALLS = get_env_int("MAX_PLANNING_TOOL_CALLS", 2)
    planning_tool_calls_used = 0
    plan_prompt_template = load_prompt("swe_generator/generate_plan.prompt")
    plan_prompt = plan_prompt_template.render(
        request_specific_part=request_specific_part,
        mcp_doc=mcp_doc,
        tavily_search_tool_name=tavily_search_tool.name,
        tavily_search_tool_description=tavily_search_tool.description,
        max_planning_tool_calls=MAX_PLANNING_TOOL_CALLS
    )
    
    planning_messages = [HumanMessage(content=plan_prompt)]
    plan = None

    for i in range(MAX_PLANNING_TURNS):
        logger.info(f"Planning turn {i + 1}/{MAX_PLANNING_TURNS} (Tool calls used: {planning_tool_calls_used}/{MAX_PLANNING_TOOL_CALLS})")
        try:
            response_message = await planning_llm.ainvoke(planning_messages)
            response_message = _normalize_and_extract_tool_calls(response_message)
        except Exception as e:
            logger.error(f"LLM invocation failed during planning phase: {e}", exc_info=True)
            return {**state, "error": f"LLM invocation failed during planning: {e}", "next_step": "error_handler"}
            
        planning_messages.append(response_message)

        if response_message.tool_calls:
            planning_tool_calls_used += len(response_message.tool_calls)
            tool_messages_to_add = []
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id")
                
                try:
                    logger.info(f"Executing planning tool '{tool_name}':")
                    agent_logger.log(event_type="tool_call", tool=tool_name, args=tool_args, call_id=tool_id)
                    
                    tool_to_execute = next((t for t in planning_tools if t.name == tool_name), None)
                    
                    if not tool_to_execute:
                        tool_output = f"Error: LLM called unhandled tool: {tool_name}"
                        logger.warning(tool_output)
                    else:
                        tool_output = await tool_to_execute.ainvoke(tool_args)

                    logger.info(f"  - Execution result: {tool_output}")
                    agent_logger.log(event_type="tool_result", tool=tool_name, output=str(tool_output), call_id=tool_id)
                    
                    final_output_with_round_info = f"Tool '{tool_name}' output:\n{str(tool_output)}"
                    if planning_tool_calls_used >= MAX_PLANNING_TOOL_CALLS:
                        final_output_with_round_info += f"\n\n[INFO] You have used {planning_tool_calls_used}/{MAX_PLANNING_TOOL_CALLS} tool calls. You must now generate the final plan based on the information you have gathered."

                    tool_messages_to_add.append(ToolMessage(content=final_output_with_round_info, tool_call_id=tool_id))
                except Exception as e:
                    error_msg = f"Error executing planning tool {tool_name}: {e}"
                    logger.error(error_msg)
                    agent_logger.log(event_type="planning_tool_error", tool=tool_name, error=str(e))
                    tool_messages_to_add.append(ToolMessage(content=error_msg, tool_call_id=tool_id))
            planning_messages.extend(tool_messages_to_add)
        else:
            plan_content = response_message.content
            # 根据模型类型进行特殊处理
            if swe_model and 'gemini' in swe_model.lower():
                logger.info(f"Detected Gemini model response in planning phase, applying special processing")
                # 处理 Gemini 模型的思考型输出，移除 <thought>...</thought> 部分
                if '<thought>' in plan_content:
                    # 尝试提取思考后的实际输出
                    thought_match = re.search(r'<thought>.*?</thought>(.*)', plan_content, re.DOTALL)
                    if thought_match:
                        plan_content = thought_match.group(1).strip()
                    else:
                        # 如果无法提取，则直接移除整个思考部分
                        plan_content = re.sub(r'<thought>.*?</thought>', '', plan_content, flags=re.DOTALL).strip()
            
            # Relaxed condition: As long as the critical "MCP Tools Plan" section is present, accept the plan.
            logger.info("Successfully generated development plan (found 'MCP Tools Plan').")
            plan = plan_content
            agent_logger.log(event_type="plan_generated", plan=plan)
            break
    if not plan:
        logger.error("Failed to generate a plan within the allowed turns.")
        return {**state, "error": "Failed to generate a plan within the allowed turns.", "next_step": "error_handler"}

    # Save the generated plan to the project directory
    try:
        # Use a path relative to the tool's workspace to avoid path duplication
        relative_plan_path = tool_relative_project_dir / "plan.md"
        await save_file_tool.ainvoke({
            "file_path": str(relative_plan_path),
            "content": plan
        })
        # Log the full path for clarity, assuming save_file_tool's root is 'workspace'
        absolute_plan_path = workspace_dir.resolve() / relative_plan_path
        logger.info(f"Development plan saved to: {absolute_plan_path}")
        agent_logger.log(event_type="plan_saved", path=str(absolute_plan_path))
    except Exception as e:
        logger.warning(f"Could not save the plan.md file: {e}")

    # --- Phase 2: Code Generation ---
    logger.info("--- Starting SWE Code Generation Phase ---")
    agent_logger.log(event_type="start_code_generation_phase")

    tools = [save_file_tool, context7_docs_tool, tavily_search_tool]
    agent_llm = base_llm.bind_tools(tools)
    logger.info(f"SWE-Agent has been equipped with tools: {[tool.name for tool in tools]}")

    MAX_CODEGEN_TURNS = get_env_int("MAX_CODEGEN_TURNS", 5)
    MAX_CODEGEN_TOOL_CALLS = get_env_int("MAX_CODEGEN_TOOL_CALLS", 3)
    codegen_tool_calls_used = 0
    code_gen_prompt_template = load_prompt("swe_generator/generate_code_from_plan.prompt")

    prompt = code_gen_prompt_template.render(
        plan=plan,
        request_specific_part=request_specific_part,
        mcp_doc=mcp_doc,
        api_name=api_name or "custom_mcp_server",
        tavily_search_tool_name=tavily_search_tool.name,
        tavily_search_tool_description=tavily_search_tool.description,
        save_file_tool_name=save_file_tool.name,
        save_file_tool_description=save_file_tool.description,
        context7_docs_tool_name=context7_docs_tool.name,
        context7_docs_tool_description=context7_docs_tool.description,
        relative_save_path=str(relative_save_path),
        max_tool_calls=MAX_CODEGEN_TOOL_CALLS
    )

    messages = [HumanMessage(content=prompt)]
    saved_code = False
    for i in range(MAX_CODEGEN_TURNS):
        logger.info(f"Generation turn {i+1}/{MAX_CODEGEN_TURNS} (Tool calls used: {codegen_tool_calls_used}/{MAX_CODEGEN_TOOL_CALLS})")

        try:
            response_message = await agent_llm.ainvoke(messages)
            response_message = _normalize_and_extract_tool_calls(response_message)
        except Exception as e:
            logger.error(f"LLM invocation failed during code generation phase: {e}", exc_info=True)
            return {**state, "error": f"LLM invocation failed during code generation: {e}", "next_step": "error_handler"}

        if response_message.tool_calls:
            messages.append(response_message)
            codegen_tool_calls_used += len(response_message.tool_calls)
            tool_messages_to_add = []
            final_update = None

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id")
                
                try:
                    logger.info(f"Executing tool '{tool_name}':")
                    agent_logger.log(event_type="tool_call", tool=tool_name, args=tool_args, call_id=tool_id)
                    
                    if tool_name == save_file_tool.name:
                        code_to_review = tool_args.get("content", "")
                        if not code_to_review.strip():
                            tool_output = "Error: LLM tried to save an empty file."
                            logger.warning(tool_output)
                        else:
                            # 根据模型类型进行特殊处理，确保我们处理的是纯代码
                            if swe_model and 'gemini' in swe_model.lower():
                                logger.info(f"Detected Gemini model response in code generation, applying special processing")
                                if '<thought>' in code_to_review:
                                    thought_match = re.search(r'<thought>.*?</thought>(.*)', code_to_review, re.DOTALL)
                                    if thought_match:
                                        code_to_review = thought_match.group(1).strip()
                                    else:
                                        code_to_review = re.sub(r'<thought>.*?</thought>', '', code_to_review, flags=re.DOTALL).strip()
                            
                            original_code = code_to_review
                            
                            # --- 1. Define and Save Backup File ---
                            # 明确定义备份文件路径，确保与最终文件不同
                            backup_file_name = f"{api_name}_original.py"
                            relative_backup_path = tool_relative_project_dir / backup_file_name
                            try:
                                await save_file_tool.ainvoke({
                                    "file_path": str(relative_backup_path),
                                    "content": original_code
                                })
                                logger.info(f"✅ Saved pre-review code backup to: {relative_backup_path}")
                            except Exception as e:
                                logger.warning(f"Could not save pre-review backup file: {e}")

                            # --- 2. Code Review and Final Save Logic ---
                            final_code_to_save = original_code  # 默认使用原始代码
                            logger.info("--- Intercepting save_file: Starting Code Review Phase ---")
                            agent_logger.log(event_type="start_code_review", code=original_code)

                            try:
                                review_prompt_template = load_prompt("swe_generator/review_and_correct.prompt")
                                review_prompt = review_prompt_template.render(code=original_code)
                                
                                code_review_llm = get_llm_for_agent(f"SWE-Agent-{api_name}-Reviewer", model_override=swe_model)
                                if not code_review_llm:
                                    raise ValueError("Could not create LLM for code review.")

                                review_response = await code_review_llm.ainvoke([HumanMessage(content=review_prompt)])
                                corrected_code_raw = review_response.content.strip()

                                # Process the corrected code (Gemini thoughts, markdown extraction)
                                if swe_model and 'gemini' in swe_model.lower():
                                    logger.info(f"Detected Gemini model response in code review, applying special processing")
                                    if '<thought>' in corrected_code_raw:
                                        thought_match = re.search(r'<thought>.*?</thought>(.*)', corrected_code_raw, re.DOTALL)
                                        corrected_code_raw = thought_match.group(1).strip() if thought_match else re.sub(r'<thought>.*?</thought>', '', corrected_code_raw, flags=re.DOTALL).strip()
                                
                                code_match = re.search(r'```python\n(.*?)\n```', corrected_code_raw, re.DOTALL)
                                corrected_code = code_match.group(1).strip() if code_match else corrected_code_raw.replace("```python", "").replace("```", "").strip()

                                if corrected_code and corrected_code.strip() and corrected_code != original_code:
                                    final_code_to_save = corrected_code
                                    logger.info("--- Finished Code Review Phase: Code was corrected. ---")
                                    agent_logger.log(event_type="code_reviewed_and_corrected", corrected_code=corrected_code)
                                else:
                                    logger.info("--- Finished Code Review Phase: No corrections needed. ---")
                                    agent_logger.log(event_type="code_reviewed_no_change")
                            
                            except Exception as e:
                                logger.error(f"⚠️ Code review failed: {e}. Proceeding with the original code.", exc_info=True)
                                agent_logger.log(event_type="code_review_failed", error=str(e))
                                # final_code_to_save 已经默认为 original_code，无需操作

                            # --- 3. Execute the final save with the determined code ---
                            logger.info(f"Saving final code to the main server file: {relative_save_path}")
                            final_save_args = {
                                "file_path": str(relative_save_path),
                                "content": final_code_to_save
                            }
                            tool_output = await save_file_tool.ainvoke(final_save_args)
                            
                            # 更新 tool_args 以便日志和状态更新
                            tool_args['content'] = final_code_to_save
                    else:
                        # --- Handle other tools normally ---
                        tool_to_execute = next((t for t in tools if t.name == tool_name), None)
                        if tool_to_execute:
                            tool_output = await tool_to_execute.ainvoke(tool_args)
                        else:
                            tool_output = f"Error: LLM called unhandled tool: {tool_name}"
                            logger.warning(tool_output)
                    logger.info(f"  - Execution result: {tool_output}")
                    agent_logger.log(event_type="tool_result", tool=tool_name, output=str(tool_output), call_id=tool_id)
                    
                    # --- After any tool call, prepare message and check for exit ---
                    final_output_with_round_info = str(tool_output)
                    if codegen_tool_calls_used >= MAX_CODEGEN_TOOL_CALLS:
                        final_output_with_round_info += f"\n\n[INFO] You have used {codegen_tool_calls_used}/{MAX_CODEGEN_TOOL_CALLS} tool calls. You MUST now provide the final response to the user's request."

                    tool_messages_to_add.append(ToolMessage(content=final_output_with_round_info, tool_call_id=tool_id))
                    
                    if tool_name == save_file_tool.name:
                        logger.info(f"Tool '{save_file_tool.name}' executed. Preparing to exit node.")
                        saved_code = True

                        # Determine the next step based on interactive mode
                        interactive_mode = state.get("interactive_mode", True)
                        next_node = "human_confirmation" if interactive_mode else "server_test"

                        final_update = {
                            "server_code": tool_args["content"],
                            "server_file_path": str(absolute_server_path),
                            "project_dir": str(project_dir.resolve()),
                            "api_name": api_name,
                            "next_step": next_node,
                            "log_files": log_files
                        }
                        # No need to add tool message, we are exiting
                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {e}"
                    logger.error(error_msg, exc_info=True)
                    agent_logger.log(event_type="tool_error", tool=tool_name, error=str(e), call_id=tool_id)
                    tool_messages_to_add.append(ToolMessage(content=error_msg, tool_call_id=tool_id))

            messages.extend(tool_messages_to_add)
            
            if saved_code:
                next_node_for_log = final_update.get('next_step')
                logger.info(f"✅ Code generation complete. Server file path: {final_update.get('server_file_path')}")
                logger.info(f"Routing to '{next_node_for_log}' next.")
                agent_logger.log(event_type="end_node", update=final_update)
                return {**state, **final_update}
        else:
            # This is a corrective measure. If the LLM responds without a tool call,
            # but it should have called save_file, we give it another chance or fail.
            final_content = response_message.content
            logger.warning(f"LLM responded without a tool call. Checking content for code. {final_content}")
            
            # Check if the content looks like it contains the final code
            if "import" in final_content:
                logger.info("Injecting a 'no_tool_call_correction' message to prompt the LLM to use save_content_to_file.")
                correction_prompt = (
                    "You have provided the code, but you did not use the 'save_content_to_file' tool to save it. "
                    "You **must** call the 'save_content_to_file' tool with the complete code in the 'content' parameter. "
                    "Do not respond with any other text, just the tool call."
                )
                messages.append(AIMessage(content=final_content)) # Add the LLM's response
                messages.append(HumanMessage(content=correction_prompt)) # Add our correction
                continue # Go to the next loop iteration immediately
            else:
                logger.error("LLM finished its turn with no tool calls and no code block. Failing.")
                logger.error(f"LLM response: {response_message.content}")
                logger.error(f"LLM response: {response_message.dict}")
                messages.append(response_message)
    
    # This part is reached if the loop completes without `saved_code` being True
    logger.error("Code generation loop finished without a successful save.")
    return {**state, "error": "Code generation failed after maximum turns.", "next_step": "error_handler"}


async def generate_server_name_from_user_input(user_input: str, swe_model: str) -> str:
    """
    Generates a suitable API name from the user's natural language input using an LLM.
    
    Args:
        user_input: The user's natural language request.
        swe_model: The name of the model to use for generating the server name.
        
    Returns:
        A short, descriptive, file-system-safe name for the server.
    """
    logger.info(f"Generating server name from user input using LLM: '{user_input[:50]}...'")
    
    prompt_template = load_prompt("swe_generator/generate_server_name.prompt")
    prompt = prompt_template.render(user_input=user_input)

    try:
        # The name generator should also use the specified SWE model for consistency.
        name_generator_llm = get_llm_for_agent(f"SWE-Agent-name_generator", model_override=swe_model)
        if not name_generator_llm:
            raise ValueError("Could not initialize LLM for name generation.")

        response = await name_generator_llm.ainvoke([HumanMessage(content=prompt)])
        raw_name = response.content.strip()
        
        # 根据模型类型进行特殊处理
        if swe_model and 'gemini' in swe_model.lower():
            logger.info(f"Detected Gemini model response, applying special processing")
            # 处理 Gemini 模型的思考型输出，移除 <thought>...</thought> 部分
            if '<thought>' in raw_name:
                # 尝试提取思考后的实际输出
                thought_match = re.search(r'<thought>.*?</thought>(.*)', raw_name, re.DOTALL)
                if thought_match:
                    raw_name = thought_match.group(1).strip()
                else:
                    # 如果无法提取，则直接移除整个思考部分
                    raw_name = re.sub(r'<thought>.*?</thought>', '', raw_name, flags=re.DOTALL).strip()
        
        # Sanitize the name to be file-system and module safe (ASCII only)
        sanitized_name = raw_name.lower()
        sanitized_name = re.sub(r'[\s-]+', '_', sanitized_name)
        # Forcefully remove any non-ASCII characters and anything not a-z, 0-9, or underscore.
        sanitized_name = re.sub(r'[^a-z0-9_]', '', sanitized_name)
        sanitized_name = sanitized_name.strip('_') # Remove leading/trailing underscores
        sanitized_name = sanitized_name[:30]
        
        logger.info(f"LLM generated raw name: '{raw_name}'. Sanitized to: '{sanitized_name}'")
        
        # If sanitization results in an empty string, fallback to simple generation
        if not sanitized_name:
            logger.warning("LLM name was empty after sanitization. Falling back to simple name generation.")
            raise ValueError("LLM returned a name that was empty after sanitization.")

        return sanitized_name
    except Exception as e:
        logger.error(f"Error generating server name with LLM: {e}. Falling back to simple implementation.", exc_info=True)
        words = user_input.split()[:3]
        name = "_".join(words).lower()
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        return name[:20] if len(name) > 20 else name