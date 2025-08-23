from typing import Any, Dict, List, Optional, Union, Callable
import asyncio
from langchain_core.tools import BaseTool, ToolException
from pydantic.v1 import BaseModel, Field
from langchain_core.messages import ToolMessage
from mcp import ClientSession
from mcp.types import TextContent
import json

from framwork.logger import logger

class MCPToolAdapter(BaseTool):
    """Adapts MCP tools to LangChain tool format"""
    
    name: str = Field(description="The name of the tool")
    description: str = Field(description="The description of the tool")
    args_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema of tool parameters")
    max_output_length: int = Field(default=2000, description="Maximum length of tool return results")
    
    # Use getter/setter to handle session attributes
    _session: Optional[ClientSession] = None
    ainvoke_override: Optional[Callable] = None
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        parameters: Dict[str, Any], 
        session: Optional[ClientSession],
        max_output_length: int = 2000,
        ainvoke_override: Optional[Callable] = None
    ):
        """Initialize MCP tool adapter"""
        super().__init__(
            name=name,
            description=description,
            args_schema=parameters
        )
        self._session = session
        self.max_output_length = max_output_length
        self.ainvoke_override = ainvoke_override
    
    def _run(self, **kwargs) -> str:
        """Synchronous execution of MCP tool call (to satisfy BaseTool's abstract method requirement)"""
        raise NotImplementedError("Only asynchronous execution is supported, please use _arun method.")
    
    def _truncate_output(self, output: str) -> str:
        """Truncate overly long output results
        
        Args:
            output: Original output result
            
        Returns:
            Truncated output result, if length exceeds limit, truncation notice will be appended
        """
        if len(output) <= self.max_output_length:
            return output
            
        truncated = output[:self.max_output_length]
        remaining_length = len(output) - self.max_output_length
        truncation_msg = f"\n\n[Output truncated, {remaining_length} characters remaining not displayed. Total length: {len(output)}]"
        return truncated + truncation_msg
    
    async def _arun(self, **kwargs) -> str:
        """Asynchronous execution of MCP tool call"""
        # Prioritize using override ainvoke method
        if self.ainvoke_override:
            return await self.ainvoke_override(kwargs)

        if not self._session:
            raise ToolException("MCP session not initialized")
            
        try:
            logger.info(f"🔧 Executing MCP tool '{self.name}' with parameters: {kwargs}")
            
            # Add parameter type conversion
            converted_args = {}
            for key, value in kwargs.items():
                # Check parameter schema to determine expected type
                param_schema = self.args_schema.get("properties", {}).get(key, {})
                expected_type = param_schema.get("type", "string")
                
                # If expecting string but received number, perform conversion
                if expected_type == "string" and isinstance(value, (int, float)):
                    converted_args[key] = str(value)
                    logger.debug(f"Parameter '{key}' converted from {type(value).__name__} to string")
                else:
                    converted_args[key] = value
            
            # Call MCP tool with converted parameters
            result = await self._session.call_tool(self.name, converted_args)
            
                
            # Extract text content from result
            content_str = ", ".join(
                item.text for item in result.content if isinstance(item, TextContent)
            )
            
            # --- Smart truncation logic ---
            original_length = len(content_str)
            if original_length > self.max_output_length:
                logger.info(f"⚠️ MCP tool '{self.name}' returned result too long ({original_length} characters), will attempt smart truncation.")
                try:
                    # Try to parse result as JSON
                    data = json.loads(content_str)
                    
                    # If it's JSON, intelligently truncate its contents
                    was_truncated = False
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 3:
                                data[key] = value[:3] # Keep only first 3 elements of list
                                was_truncated = True
                                logger.info(f"  - Truncated list '{key}' to first 3 elements.")
                            elif isinstance(value, str) and len(value) > 1000:
                                data[key] = value[:1000] + "..." # Truncate long strings
                                was_truncated = True
                                logger.info(f"  - Truncated string '{key}'.")
                    
                    if was_truncated:
                        data["__truncation_alert__"] = "This JSON object has been intelligently truncated to save space. Lists may be shortened."
                        # Add explicit adapter truncation marker
                        data["__adapter_truncation_note__"] = "NOTE: This truncation is due to the MCP adapter's output length limit, NOT an issue with the tool itself."

                    # Convert truncated JSON back to string
                    content_str = json.dumps(data, ensure_ascii=False)
                    logger.info(f"  - Successfully performed smart JSON truncation.")

                except json.JSONDecodeError:
                    # If not JSON, perform original brute force truncation
                    logger.info(f"  - Content is not JSON, performing standard text truncation.")
                    truncated = content_str[:self.max_output_length]
                    remaining_length = len(content_str) - self.max_output_length
                    # Add explicit adapter truncation marker
                    truncation_msg = f"\n\n[ADAPTER_TRUNCATION_NOTE: Output truncated by MCP adapter, this is an adapter limitation not a tool issue. {remaining_length} characters remaining not displayed. Total length: {len(content_str)}]"
                    content_str = truncated + truncation_msg
            
            # --- Hard length limit check ---
            hard_limit = self.max_output_length + 1000
            if len(content_str) > hard_limit:
                logger.warning(f"  - Length after smart truncation ({len(content_str)}) still exceeds hard limit ({hard_limit}), will perform final truncation.")
                content_str = content_str[:hard_limit] + f"\n\n[ADAPTER_TRUNCATION_NOTE: Output hard truncated by MCP adapter, this is an adapter limitation not a tool issue. Original length: {original_length}]"

            logger.info(f"✅ MCP tool '{self.name}' executed successfully: {content_str}")
            return content_str or "No output returned."
            
        except Exception as e:
            error_msg = f"❌ MCP tool '{self.name}' execution failed: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}" 