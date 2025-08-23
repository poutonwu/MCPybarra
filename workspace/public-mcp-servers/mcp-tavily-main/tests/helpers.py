"""Test helpers for extracting handlers from the server module."""
import asyncio
import inspect
from unittest.mock import patch, MagicMock, AsyncMock
import mcp_server_tavily.server as server_module


class ServerHandlerExtractor:
    """Extract handler functions from the server module."""
    
    def __init__(self):
        self.handlers = {}
        
    async def extract_handlers(self):
        """Extract all handler functions from the server module."""
        # Create mocks for all decorators
        with patch('mcp_server_tavily.server.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server
            
            # Mock the decorator methods to capture handlers
            def capture_handler(decorator_name):
                def decorator(func):
                    self.handlers[decorator_name] = func
                    return func
                return decorator
            
            mock_server.list_tools.side_effect = capture_handler('list_tools')
            mock_server.list_prompts.side_effect = capture_handler('list_prompts')
            mock_server.call_tool.side_effect = capture_handler('call_tool')
            mock_server.get_prompt.side_effect = capture_handler('get_prompt')
            
            # Mock stdio_server to prevent actual I/O
            with patch('mcp_server_tavily.server.stdio_server') as mock_stdio:
                mock_stdio.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
                
                # Mock TavilyClient to prevent actual API calls
                with patch('mcp_server_tavily.server.TavilyClient') as mock_client_class:
                    # Call serve to register all handlers
                    await server_module.serve("fake_api_key")
        
        return self.handlers


async def get_server_handlers():
    """Get all handler functions from the server module."""
    extractor = ServerHandlerExtractor()
    return await extractor.extract_handlers()