import json
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

from framwork.mcp_swe_flow.prompts.utils import load_prompt
from framwork.mcp_swe_flow.state import MCPWorkflowState
from framwork.mcp_swe_flow.config import llm, PROJECT_ROOT, get_llm_for_agent, get_env_int
from framwork.tool import save_file_tool, read_file_tool, tavily_search_tool, context7_docs_tool
from framwork.schema import Memory
from framwork.logger import logger, get_agent_logger

# Define the maximum number of refinement loops to prevent infinite loops
MAX_REFINE_LOOPS = get_env_int("MAX_REFINE_LOOPS", 2)
# Define the maximum number of internal thinking/research turns for the refiner
MAX_INTERNAL_TURNS = get_env_int("MAX_INTERNAL_TURNS", 5)
MAX_INTERNAL_TOOL_CALLS = get_env_int("MAX_INTERNAL_TOOL_CALLS", 3)

async def refine_code_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """
    Refines the code based on the test report and decides whether to continue testing or deliver.
    This node contains an internal loop that allows the LLM to use tools for research before making a decision.
    After the first refinement, re-testing is mandatory.
    """
    api_name = state.get("api_name")
    agent_logger = get_agent_logger(f"CodeRefiner-Agent-{api_name or 'custom'}")

    # Add the logger's file path to the state for aggregation later.
    # This is the ONLY logger instance for this node.
    log_files = state.get("log_files", [])
    if agent_logger.log_path and str(agent_logger.log_path) not in log_files:
        log_files.append(str(agent_logger.log_path))

    try:
        # --- Debug Log: Checking incoming state ---
        logger.debug(f"Entered refine_code_node. Received state keys: {list(state.keys())}")
        
        refinement_loop_count = state.get("refinement_loop_count", 0) + 1
        logger.info(f"--- Code Refinement Cycle {refinement_loop_count}/{MAX_REFINE_LOOPS} ---")
        agent_logger.log(event_type="start_node", state={"refinement_loop_count": refinement_loop_count})

        # Get necessary information from state
        server_code = state.get("server_code")
        test_report = state.get("test_report_content")
        mcp_doc = state.get("mcp_doc")
        server_file_path_str = state.get("server_file_path")
        project_dir_str = state.get("project_dir") # Get the stable project root directory

        server_file_path = Path(server_file_path_str)
        project_dir = Path(project_dir_str) # Use the stable project directory
        
        # --- Stage 1: Initial Assessment (Decide if refinement is needed) ---
        logger.info("--- Stage 1: Initial Code Assessment ---")
        agent_logger.log(event_type="start_initial_assessment")
        assessment_template = load_prompt("code_refiner/assess_deliverability.prompt")
        assessment_prompt_str = assessment_template.render(
            server_code=server_code,
            test_report_str=json.dumps(test_report, indent=2) if isinstance(test_report, dict) else str(test_report)
        )
        
        assessment_llm = get_llm_for_agent(f"CodeRefiner-Agent-{api_name or 'custom'}")
        assessment_response = await assessment_llm.ainvoke([HumanMessage(content=assessment_prompt_str)])
        
        try:
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', assessment_response.content, re.DOTALL)
            if not json_match:
                raise json.JSONDecodeError("No JSON block found in assessment response", assessment_response.content, 0)
            assessment_data = json.loads(json_match.group(1).strip())
            initial_decision = assessment_data["decision"]
            reason = assessment_data.get("reason", "No reason provided.")
            logger.info(f"Initial Assessment: {initial_decision}. Reason: {reason}")
            agent_logger.log(event_type="initial_assessment_complete", decision=initial_decision, reason=reason)
        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"Failed to parse initial assessment from LLM: {e}. Defaulting to refinement."
            logger.warning(error_msg)
            initial_decision = "NEEDS_REFINEMENT"
            reason = "Could not parse initial assessment."
            agent_logger.log(event_type="initial_assessment_failed", error=error_msg)
            # Ensure assessment_data exists even on failure, for logging purposes.
            assessment_data = {"decision": initial_decision, "reason": reason, "error_details": error_msg}

        refined_code = server_code
        decision = initial_decision
        
        is_max_refine_loops = refinement_loop_count >= MAX_REFINE_LOOPS

        # --- Stage 2: In-depth Refinement (if necessary) ---
        if initial_decision == "NEEDS_REFINEMENT" and not is_max_refine_loops:
            logger.info("--- Stage 2: Entering In-depth Code Refinement Loop ---")
            agent_logger.log(event_type="start_refinement_loop")
            tools = [save_file_tool, tavily_search_tool, context7_docs_tool]
            refiner_llm = get_llm_for_agent(f"CodeRefiner-Agent-{api_name or 'custom'}").bind_tools(tools)

            refine_prompt_template = load_prompt("code_refiner/refine_with_tools.prompt")
            refine_prompt = refine_prompt_template.render(
                server_file_name=server_file_path.name,
                server_code=server_code,
                tavily_search_tool_name=tavily_search_tool.name,
                tavily_search_tool_description=tavily_search_tool.description,
                save_file_tool_name=save_file_tool.name,
                save_file_tool_description=save_file_tool.description,
                context7_docs_tool_name=context7_docs_tool.name,
                context7_docs_tool_description=context7_docs_tool.description,
                test_report_str=json.dumps(test_report, indent=2, ensure_ascii=False) if isinstance(test_report, dict) else str(test_report),
                mcp_doc=mcp_doc,
                max_tool_calls=MAX_INTERNAL_TOOL_CALLS
            )

            memory = Memory()
            memory.add_message(HumanMessage(content=refine_prompt))
            
            # --- Internal Loop: Refinement with Tools ---
            decision_data = None
            internal_tool_calls_used = 0
            for i in range(MAX_INTERNAL_TURNS):
                logger.info(f"Refiner internal research turn {i + 1}/{MAX_INTERNAL_TURNS} (Tool calls used: {internal_tool_calls_used}/{MAX_INTERNAL_TOOL_CALLS})")
                response_message = await refiner_llm.ainvoke(memory.messages)
                memory.add_message(response_message)

                if response_message.tool_calls:
                    internal_tool_calls_used += len(response_message.tool_calls)
                    logger.info(f"LLM requested to execute tools: {[tc['name'] for tc in response_message.tool_calls]}")
                    tool_messages = []
                    for tool_call in response_message.tool_calls:
                        agent_logger.log(event_type="tool_call", tool=tool_call["name"], args=tool_call["args"], call_id=tool_call["id"])
                        tool_to_execute = next((t for t in tools if t.name == tool_call["name"]), None)
                        if tool_to_execute:
                            try:
                                tool_output = await tool_to_execute.ainvoke(tool_call["args"])
                                
                                final_output = str(tool_output)
                                if internal_tool_calls_used >= MAX_INTERNAL_TOOL_CALLS:
                                    final_output += f"\n\n[INFO] You have used all {MAX_INTERNAL_TOOL_CALLS} tool calls. You MUST now provide the complete 'refined_code'."

                                logger.info(f"Tool output: {final_output}")
                                agent_logger.log(event_type="tool_result", tool=tool_call["name"], output=final_output, call_id=tool_call["id"])
                                tool_messages.append(ToolMessage(content=final_output, tool_call_id=tool_call["id"]))
                            except Exception as e:
                                error_msg = f"Error executing tool '{tool_call['name']}': {e}"
                                logger.error(error_msg)
                                agent_logger.log(event_type="tool_error", tool=tool_call["name"], error=error_msg, call_id=tool_call["id"])
                                tool_messages.append(ToolMessage(content=error_msg, tool_call_id=tool_call["id"]))
                        else:
                            error_msg = f"Error: Tool '{tool_call['name']}' not found."
                            logger.warning(error_msg)
                            agent_logger.log(event_type="tool_error", tool=tool_call["name"], error=error_msg, call_id=tool_call["id"])
                            tool_messages.append(ToolMessage(content=error_msg, tool_call_id=tool_call["id"]))
                    
                    memory.add_messages(tool_messages)
                    continue

                response_content = response_message.content
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_content, re.DOTALL)
                if json_match:
                    try:
                        decision_data_candidate = json.loads(json_match.group(1).strip())
                        # The refiner's only job is to provide code. It no longer makes a decision.
                        if "refined_code" in decision_data_candidate:
                            
                            # --- Validation Step ---
                            refined_code_candidate = decision_data_candidate.get("refined_code")
                            if not isinstance(refined_code_candidate, str) or not refined_code_candidate.strip() or refined_code_candidate.strip().lower().startswith(("<", "```")):
                                error_msg = "Your previous response was invalid. The 'refined_code' field contained a placeholder or invalid content, not the full Python source code. You MUST provide the complete, raw, runnable Python code. Please correct your response."
                                logger.warning(f"Refiner LLM failed validation. Sending correction prompt. Invalid code received: '{str(refined_code_candidate)[:200]}...'")
                                agent_logger.log(event_type="refinement_validation_failed", error=error_msg)
                                memory.add_message(HumanMessage(content=error_msg))
                                continue  # Give the LLM another chance

                            # --- Validation Passed ---
                            logger.info("LLM has generated a valid final refined code.")
                            # We only care about the code here. The decision is made outside this loop.
                            refined_code = refined_code_candidate # Lock in the valid code
                            break # Exit the loop with valid data
                            
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Found JSON block but parsing failed or key fields are missing: {e}. Will continue the loop.")
                else:
                    logger.info("LLM generated an intermediate thought process, continuing the loop. Thought content：" + response_message.content)

            if refined_code == server_code: # Check if we actually got new code
                logger.error("LLM failed to generate valid refined code within the internal loop. Raising an error.")
                raise RuntimeError("LLM failed to generate valid refined code within the internal loop.")
            
            # After refinement, the decision is implicitly "NEEDS_REFINEMENT" because we will test again.
            # The 'decision' variable from the initial assessment is not updated.
            logger.info(f"✅ LLM Refinement complete. The code will now be re-tested.")
        else:
            logger.info("--- Stage 2: Skipped In-depth Refinement ---")
            # If refinement is skipped, the initial assessment's decision and reason are used.
            refined_code = server_code
            reason = assessment_data.get("reason", "No reason provided.")
            logger.info(f"Proceeding with decision '{decision}' from initial assessment. Reason: {reason}")

        # --- Stage 3: Save Artifacts and Determine Next Step ---
        logger.info("--- Stage 3: Saving Artifacts and Finalizing Step ---")
        agent_logger.log(event_type="decision_made", decision=decision, reason=reason)

        # Save the refined code (even if it's the original code, path changes)
        # Corrected path creation logic: always create the 'refined' subdirectory based on the original project_dir
        refined_dir = project_dir / "refined"
        refined_dir.mkdir(exist_ok=True)
        (refined_dir / "__init__.py").touch(exist_ok=True)
        
        # New server file path
        refined_server_path = refined_dir / "server.py"
        decision_file_path = refined_dir / "refinement_decision.json"

        workspace_dir = PROJECT_ROOT / "workspace"
        relative_save_path = refined_server_path.relative_to(workspace_dir)
        relative_decision_path = decision_file_path.relative_to(workspace_dir)

        # Save the refined code
        await save_file_tool.ainvoke({"file_path": str(relative_save_path), "content": refined_code})
        logger.info(f"💾 Refined code saved to: {refined_server_path}")

        # Always save the assessment data for the current cycle for traceability.
        final_assessment_log = {
            "final_decision_for_this_cycle": decision,
            "reasoning": reason,
            "refinement_loop_count": refinement_loop_count,
            "original_assessment": assessment_data if 'assessment_data' in locals() else "Not available"
        }
        await save_file_tool.ainvoke({"file_path": str(relative_decision_path), "content": json.dumps(final_assessment_log, indent=2, ensure_ascii=False)})
        logger.info(f"💾 Refinement assessment log saved to: {decision_file_path}")
        
        update = {
            "server_code": refined_code,
            "server_file_path": str(refined_server_path),
            "refinement_loop_count": refinement_loop_count,
            "last_refinement_reason": reason,
            "project_dir": str(project_dir),
            "api_name": api_name
        }
        
        is_deliverable = decision == "DELIVERABLE"
        is_max_refine_loops = refinement_loop_count >= MAX_REFINE_LOOPS

        # If deliverable, or if we've hit the max attempts, finalize.
        if is_deliverable or is_max_refine_loops:
            logger.info("✅ Code is ready for delivery or has reached the maximum number of retries. Entering project finalization phase.")
            if is_max_refine_loops and not is_deliverable:
                logger.warning(f"Maximum refinement attempts ({MAX_REFINE_LOOPS}) reached. Forcing delivery.")
            
            # --- Project Finalization ---
            agent_logger.log(event_type="start_project_finalization")
            # All final artifacts will be saved in the 'refined' subdirectory.
            readme_path = refined_dir / "README.md"
            requirements_path = refined_dir / "requirements.txt"
            
            workspace_dir = PROJECT_ROOT / "workspace"
            relative_readme_path = readme_path.relative_to(workspace_dir)
            relative_req_path = requirements_path.relative_to(workspace_dir)
            
            finalizer_llm = get_llm_for_agent(f"CodeRefiner-Agent-{api_name or 'custom'}")

            logger.info("📄 Generating README.md...")
            readme_template = load_prompt("code_refiner/generate_readme.prompt")
            readme_prompt = readme_template.render(refined_code=refined_code, api_name=api_name, mcp_doc=mcp_doc)
            readme_response = await finalizer_llm.ainvoke([HumanMessage(content=readme_prompt)])
            await save_file_tool.ainvoke({"file_path": str(relative_readme_path), "content": readme_response.content.strip()})
            logger.info(f"✅ README.md saved to: {readme_path}")
            agent_logger.log(event_type="readme_generated", path=str(readme_path))
            update["readme_path"] = str(readme_path)

            logger.info("📦 Generating requirements.txt...")
            req_template = load_prompt("code_refiner/generate_requirements.prompt")
            req_prompt = req_template.render(refined_code=refined_code)
            req_response = await finalizer_llm.ainvoke([HumanMessage(content=req_prompt)])
            await save_file_tool.ainvoke({"file_path": str(relative_req_path), "content": req_response.content.strip()})
            logger.info(f"✅ requirements.txt saved to: {requirements_path}")
            agent_logger.log(event_type="requirements_generated", path=str(requirements_path))
            update["requirements_path"] = str(requirements_path)
            
            update["next_step"] = "statistics_logger"
            
        else:  # NEEDS_REFINEMENT
            logger.info("🔄 Code needs further refinement. Returning to the testing phase.")
            update["next_step"] = "server_test"
            
        logger.info("--- ✅ Code Refinement Node Completed ---")
        agent_logger.log(event_type="end_node", update=update)
        update["log_files"] = log_files
        return {**state, **update}

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_message = f"A critical error occurred in the code refiner node: {e}"
        logger.error(f"❌ {error_message}\n{error_details}")
        # Return state for the error handler
        return {
            **state,
            "log_files": log_files,
            "error": error_message,
            "next_step": "error_handler",
            "error_source": "code_refiner"
        }