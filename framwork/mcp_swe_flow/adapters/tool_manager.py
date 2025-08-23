from typing import Dict, List, Any, Optional
import asyncio

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters

from framwork.logger import logger
from framwork.mcp_swe_flow.adapters.mcp_client_adapter import MCPClientAdapter

class MCPToolManager:
    """MCP tool manager, uses MCPClientAdapter to connect to servers, but uses langchain_mcp_adapters to manage tools"""
    
    def __init__(self):
        """Initialize a new MCPToolManager instance."""
        self._initialized = False
        self.client_adapter = MCPClientAdapter()
        self.lc_tools = None  # langchain_mcp_adapters tools
    
    async def initialize(self, server_params):
        """Initialize MCP server connection
        
        Args:
            server_params: StdioServerParameters object
            
        Returns:
            List of loaded langchain_mcp_adapters tools
        """
        if self._initialized:
            return self.lc_tools
        
        try:
            logger.info(f"🔌 Initializing MCP server connection: {server_params.args}")
            
            # Use MCPClientAdapter to connect to server
            await self.client_adapter.connect_stdio_with_params(server_params)
            
            # Use langchain_mcp_adapters to load tools
            self.lc_tools = await load_mcp_tools(self.client_adapter.session)
            
            self._initialized = True
            logger.info(f"✅ MCP tools loaded: {[t.name for t in self.lc_tools]}")
            
            return self.lc_tools
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_tool_names(self) -> List[str]:
        """Get list of all available tool names"""
        if not self._initialized:
            raise RuntimeError("MCPToolManager not initialized")
        return [t.name for t in self.lc_tools]
    
    def get_tool_by_name(self, tool_name: str):
        """Get tool object by name"""
        if not self._initialized:
            raise RuntimeError("MCPToolManager not initialized")
        
        tool = next((t for t in self.lc_tools if t.name == tool_name), None)
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found")
        return tool
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any], max_length: int = 1400) -> Any:
        """Generic tool invocation method
        
        Args:
            tool_name: Tool name
            params: Tool parameters
            max_length: Maximum length of returned content
            
        Returns:
            Tool execution result
        """
        if not self._initialized:
            raise RuntimeError("MCPToolManager not initialized")
        
        tool = self.get_tool_by_name(tool_name)
        
        try:
            logger.info(f"🔧 Executing MCP tool '{tool_name}' with parameters: {params}")
            result = await tool.ainvoke(params)
            
            # Handle different types of results
            if isinstance(result, dict):
                # If result is a dictionary, preserve original structure
                processed_result = result
                # If there's a content field and it's a string, truncate it
                if "content" in result and isinstance(result["content"], str):
                    content = result["content"]
                    original_length = len(content)
                    if original_length > max_length:
                        logger.info(f"⚠️ Tool returned result too long ({original_length} characters), truncated")
                        processed_result["content"] = content[:max_length] + f"...[Truncated], output truncated by MCP adapter, this is an adapter limitation not a tool issue. Total {original_length} characters, remaining {original_length - max_length} characters"

            elif isinstance(result, str):
                # If result is a string, truncate directly
                original_length = len(result)
                if original_length > max_length:
                    logger.info(f"⚠️ Tool returned result too long ({original_length} characters), truncated")
                    processed_result = result[:max_length] + f"...[Truncated], output truncated by MCP adapter, this is an adapter limitation not a tool issue. Total {original_length} characters, remaining {original_length - max_length} characters"
                else:
                    processed_result = result
            else:
                # Keep other types unchanged
                processed_result = result
            
            # Log correctly based on processed_result type
            if isinstance(processed_result, dict) and "content" in processed_result:
                logger.info(f"✅ Tool '{tool_name}' executed successfully, tool returned result: {processed_result['content']}")
            else:
                logger.info(f"✅ Tool '{tool_name}' executed successfully, tool returned result: {processed_result}")
            return processed_result
        except asyncio.CancelledError:
            logger.warning(f"🟠 Tool '{tool_name}' call was cancelled. This usually occurs during timeout or program shutdown.")
            # Re-raise exception so upper level calls (like asyncio.wait_for) can properly handle timeout
            raise
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


    async def cleanup(self):
        """Clean up resources"""
        if self._initialized:
            try:
                logger.info("🧹 Starting cleanup of MCP tool manager resources...")
                
                # Use MCPClientAdapter to disconnect
                await self.client_adapter.disconnect()
                
                self._initialized = False
                self.lc_tools = None
                logger.info("✅ MCP tool manager resources cleanup completed")
            except Exception as e:
                logger.error(f"❌ Resource cleanup failed: {type(e).__name__}: {e}")
