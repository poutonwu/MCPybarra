import pytest
import os
import asyncio
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Create a custom AsyncMock that's safer for our tests
class SafeAsyncMock:
    def __init__(self, return_value=None):
        self._return_value = return_value if return_value is not None else None
        self.call_args = None
        self.call_count = 0
        self.call_args_list = []
        
    async def __call__(self, *args, **kwargs):
        self.call_args = (args, kwargs)
        self.call_args_list.append(self.call_args)
        self.call_count += 1
        if isinstance(self._return_value, asyncio.Future):
            return await self._return_value
        elif asyncio.iscoroutine(self._return_value):
            return await self._return_value
        else:
            return self._return_value

# Load environment variables from .env file or .env.sample if .env doesn't exist
if os.path.exists(os.path.join(os.path.dirname(__file__), '.env')):
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.sample'))


@pytest.fixture
def mock_tavily_client():
    """Mock the TavilyClient to avoid real API calls during tests."""
    with patch('mcp_server_tavily.server.TavilyClient') as mock_client_class:
        client_instance = MagicMock()
        # Use regular MagicMock for synchronous methods
        client_instance.search = MagicMock()
        mock_client_class.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_server():
    """Mock the MCP Server to test server functions."""
    with patch('mcp_server_tavily.server.Server') as mock_server_class:
        server_instance = MagicMock()
        
        # Set up mocks for decorator methods
        handler_registry = {}

        def mock_decorator(name):
            def decorator(func):
                handler_registry[name] = func
                return func
            return decorator

        # Create decorator functions that return decorator functions 
        server_instance.list_tools = MagicMock(return_value=mock_decorator('list_tools'))
        server_instance.list_prompts = MagicMock(return_value=mock_decorator('list_prompts'))
        server_instance.call_tool = MagicMock(return_value=mock_decorator('call_tool'))
        server_instance.get_prompt = MagicMock(return_value=mock_decorator('get_prompt'))
        
        # For accessing the registered handlers
        server_instance.handler_registry = handler_registry
        
        # Ensure these methods are called during serve()
        server_instance.create_initialization_options = MagicMock(return_value={})
        
        # Use our SafeAsyncMock for the server.run method
        server_instance.run = SafeAsyncMock(return_value=None)
        
        mock_server_class.return_value = server_instance
        yield server_instance


@pytest.fixture
def mock_stdio_server():
    """Mock the stdio_server to test server run function."""
    with patch('mcp_server_tavily.server.stdio_server') as mock_stdio:
        # Create a context manager that can be entered and exited without error
        mock_context = MagicMock()
        
        # Create proper SafeAsyncMock that returns a future
        enter_future = asyncio.Future()
        enter_future.set_result((MagicMock(), MagicMock()))
        
        exit_future = asyncio.Future()
        exit_future.set_result(None)
        
        mock_context.__aenter__ = SafeAsyncMock(return_value=enter_future)
        mock_context.__aexit__ = SafeAsyncMock(return_value=exit_future)
        mock_stdio.return_value = mock_context
        yield mock_stdio


@pytest.fixture
def server_handlers(mock_server):
    """Return the registered handlers after calling serve."""
    import asyncio
    from mcp_server_tavily.server import serve
    # Run serve to register all handlers
    asyncio.run(serve("fake_api_key"))
    return mock_server.handler_registry


@pytest.fixture
def web_search_response():
    """Sample response for web search."""
    return {
        "results": [
            {
                "title": "Sample Result 1",
                "url": "https://example.com/1",
                "content": "This is sample content from the first result."
            },
            {
                "title": "Sample Result 2",
                "url": "https://example.com/2",
                "content": "This is sample content from the second result."
            }
        ]
    }


@pytest.fixture
def answer_search_response():
    """Sample response for answer search."""
    return {
        "answer": "This is a sample answer.",
        "results": [
            {
                "title": "Sample Result 1",
                "url": "https://example.com/1",
                "content": "This is sample content from the first result."
            },
            {
                "title": "Sample Result 2",
                "url": "https://example.com/2",
                "content": "This is sample content from the second result."
            }
        ]
    }


@pytest.fixture
def news_search_response():
    """Sample response for news search."""
    return {
        "results": [
            {
                "title": "Sample News 1",
                "url": "https://example.com/news/1",
                "content": "This is sample content from the first news result.",
                "published_date": "2023-09-01"
            },
            {
                "title": "Sample News 2",
                "url": "https://example.com/news/2",
                "content": "This is sample content from the second news result.",
                "published_date": "2023-09-02"
            }
        ]
    }