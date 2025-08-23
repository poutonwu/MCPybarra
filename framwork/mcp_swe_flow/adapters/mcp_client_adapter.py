from builtins import ExceptionGroup
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
import asyncio
import httpx

from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from mcp.shared.exceptions import McpError

from framwork.logger import logger
from framwork.mcp_swe_flow.adapters import MCPToolAdapter

class MCPClientAdapter:
    """
    An adapter for simplifying STDIO connections with MCP servers.
    Each instance manages an independent server connection.
    """
    def __init__(self):
        """Initialize a new MCPClientAdapter instance."""
        self.session: Optional[ClientSession] = None
        self.process = None
        self._lock = asyncio.Lock()
        self._initialized = False
        self.exit_stack = AsyncExitStack()
        self.tools: List[MCPToolAdapter] = []
        
    async def _send_http_request(self, server_url: str, method: str, params: Dict[str, Any]) -> Any:
        """Send a JSON-RPC 2.0 HTTP POST request with custom headers using httpx"""
        headers = {
            "X-Context7-Source": "mcp-server",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        json_rpc_payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(server_url, json=json_rpc_payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                response_json = response.json()
                if "error" in response_json:
                    raise McpError(f"JSON-RPC Error from server: {response_json['error']}")
                return response_json.get("result")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP request failed: {e.response.status_code} - {e.response.text}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Error sending HTTP request: {e}", exc_info=True)
                raise

    async def connect_stdio(self, module_name: str, cwd: Optional[Path] = None, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """Connect to MCP server via STDIO
        
        Args:
            module_name: Module name (e.g., "output-servers.mcp-chucknorris")
            cwd: Working directory, defaults to current directory
            max_output_length: Maximum length of tool return results, defaults to 1200 characters
            
        Returns:
            List of adapted LangChain tools
        """
        if self.session:
            await self.disconnect()
            
        try:
            logger.info(f"🔌 Connecting to MCP server module: {module_name}")
            
            # Prepare parameters
            command = sys.executable
            args = ["-m", module_name]
            cwd_str = str(cwd) if cwd else None
            
            logger.info(f"🔄 Preparing startup command: {command} {' '.join(args)}, cwd={cwd_str}")
            
            # Use the same method as framwork/tool/mcp.py
            server_params = StdioServerParameters(command=command, args=args)
            logger.info(f"🔄 Creating server parameters: {server_params}")
            
            # Start and connect to MCP server via subprocess
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logger.info(f"✅ MCP server connection successful")
            
            # Initialize session
            await self.session.initialize()
            logger.info("✅ MCP session initialization successful")
            
            self._initialized = True
            
            # Get and convert tools
            return await self.load_tools(max_output_length=max_output_length)
            
        except Exception as e:
            logger.error(f"❌ MCP server connection failed: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            if self.session:
                await self.disconnect()
            raise

    async def load_tools(self, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """Load tools from MCP server and convert them to LangChain tools
        
        Args:
            max_output_length: Maximum length of tool return results, defaults to 1200 characters
            
        Returns:
            List of adapted LangChain tools
        """
        if not self.session:
            raise RuntimeError("MCP session not initialized")
            
        try:
            # Get tool list
            response = await self.session.list_tools()
            logger.info(f"📋 Retrieved {len(response.tools)} tools from MCP server")
            
            # Clear existing tools
            self.tools = []
            
            # Convert tools
            for tool in response.tools:
                try:
                    # Create adapter
                    adapter = MCPToolAdapter(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.inputSchema,
                        session=self.session,
                        max_output_length=max_output_length
                    )
                    self.tools.append(adapter)
                    logger.info(f"✅ Successfully converted tool: {tool.name}")
                except Exception as e:
                    logger.error(f"❌ Tool {tool.name} conversion failed: {e}", exc_info=True)
            
            logger.info(f"🧰 Converted {len(self.tools)} tools total: {[tool.name for tool in self.tools]}")
            return self.tools
            
        except Exception as e:
            logger.error(f"❌ Tool loading failed: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server and clean up resources."""
        async with self._lock:
            if not self._initialized:
                return

            logger.info("👋 Disconnecting from MCP server...")
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                logger.warning(f"🟠 Ignorable error occurred during disconnection (usually at test end): {type(e).__name__}", exc_info=True)
            finally:
                self.session = None
                self.process = None
                self._initialized = False
                self.tools = []
                self.exit_stack = AsyncExitStack()
                logger.info("👋 MCP server connection disconnected") 

    async def connect_stdio_with_params(self, server_params: StdioServerParameters, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """Connect to MCP server via passed StdioServerParameters
        
        Args:
            server_params: STDIO startup parameters for MCP server
            max_output_length: Maximum length of tool return results, defaults to 1200 characters
            
        Returns:
            List of adapted LangChain tools
        """
        if self.session:
            await self.disconnect()
            
        try:
            logger.info(f"🔌 Connecting to MCP server via preset parameters: {server_params}")
            
            # Start and connect to MCP server via subprocess
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logger.info(f"✅ MCP server connection successful")
            
            # Initialize session
            await self.session.initialize()
            logger.info("✅ MCP session initialization successful")
            
            self._initialized = True
            
            # Get and convert tools
            return await self.load_tools(max_output_length=max_output_length)
            
        except Exception as e:
            logger.error(f"❌ MCP server connection failed: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            if self.session:
                await self.disconnect()
            raise

    async def connect_stdio_file(self, file_path: str, cwd: Optional[Path] = None, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """Connect to MCP server by directly running Python file
        
        Args:
            file_path: Path to Python file (e.g., "workspace/pipeline-output-servers/gemini-2.5-pro/mcp_word_document_processor/mcp_word_document_processor.py")
            cwd: Working directory, defaults to current directory
            max_output_length: Maximum length of tool return results, defaults to 1200 characters
            
        Returns:
            List of adapted LangChain tools
        """
        if self.session:
            await self.disconnect()
            
        try:
            logger.info(f"🔌 Connecting to MCP server via file path: {file_path}")
            
            # Ensure file path exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"MCP server file does not exist: {file_path}")
            
            # Prepare parameters
            command = sys.executable
            args = [file_path]  # Directly run Python file
            cwd_str = str(cwd) if cwd else None
            
            logger.info(f"🔄 Preparing startup command: {command} {' '.join(args)}, cwd={cwd_str}")
            
            # Use the same method as framwork/tool/mcp.py
            server_params = StdioServerParameters(command=command, args=args)
            logger.info(f"🔄 Creating server parameters: {server_params}")
            
            # Start and connect to MCP server via subprocess
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logger.info(f"✅ MCP server connection successful")
            
            # Initialize session
            await self.session.initialize()
            logger.info("✅ MCP session initialization successful")
            
            self._initialized = True
            
            # Get and convert tools
            return await self.load_tools(max_output_length=max_output_length)
            
        except Exception as e:
            logger.error(f"❌ MCP server connection failed: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            if self.session:
                await self.disconnect()
            raise 