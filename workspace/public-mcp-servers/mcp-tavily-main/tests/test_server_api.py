import pytest
from unittest.mock import MagicMock, patch, call
import asyncio
import inspect
from mcp.types import Tool, TextContent, GetPromptResult, PromptMessage
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, INTERNAL_ERROR
from tavily import InvalidAPIKeyError, UsageLimitExceededError
from mcp.server import Server

# Create a custom AsyncMock that's safer for our tests
class SafeAsyncMock:
    def __init__(self, return_value=None):
        self._return_value = return_value if return_value is not None else None
        self.call_args = None
        self.call_count = 0
        self.call_args_list = []
        
    async def __call__(self, *args, **kwargs):
        self.call_args = call(*args, **kwargs)
        self.call_args_list.append(self.call_args)
        self.call_count += 1
        if isinstance(self._return_value, asyncio.Future):
            return await self._return_value
        elif asyncio.iscoroutine(self._return_value):
            return await self._return_value
        else:
            return self._return_value

# Import the server module directly
import mcp_server_tavily.server as server_module

# Patch the stdio_server to avoid actual I/O operations
stdio_mock = patch('mcp_server_tavily.server.stdio_server', autospec=True).start()

# Create proper SafeAsyncMock for aenter
enter_future = asyncio.Future()
enter_future.set_result((MagicMock(), MagicMock()))
enter_mock = SafeAsyncMock(return_value=enter_future)

# Create proper SafeAsyncMock for aexit
exit_future = asyncio.Future()
exit_future.set_result(None)
exit_mock = SafeAsyncMock(return_value=exit_future)

# Apply the mocks
stdio_context = MagicMock()
stdio_context.__aenter__ = enter_mock
stdio_context.__aexit__ = exit_mock
stdio_mock.return_value = stdio_context


@pytest.mark.asyncio
class TestServerListTools:
    async def test_list_tools(self, server_handlers):
        """Test that the list_tools handler returns the expected tools."""
        # Get the registered list_tools handler
        list_tools_handler = server_handlers['list_tools']
        
        # Call the function
        tools = await list_tools_handler()
        
        # Verify that we get 3 tools as expected
        assert len(tools) == 3
        
        # Check that the tool names are correct
        tool_names = [tool.name for tool in tools]
        assert "tavily_web_search" in tool_names
        assert "tavily_answer_search" in tool_names
        assert "tavily_news_search" in tool_names
        
        # Check that each tool has a description and schema
        for tool in tools:
            assert isinstance(tool, Tool)
            assert tool.description
            assert tool.inputSchema


@pytest.mark.asyncio
class TestServerListPrompts:
    async def test_list_prompts(self, mock_server):
        """Test that the list_prompts handler returns the expected prompts."""
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.list_prompts()
        list_prompts_handler = mock_server.handler_registry['list_prompts']
        
        # Call the function
        prompts = await list_prompts_handler()
        
        # Verify that we get 3 prompts as expected
        assert len(prompts) == 3
        
        # Check that the prompt names are correct
        prompt_names = [prompt.name for prompt in prompts]
        assert "tavily_web_search" in prompt_names
        assert "tavily_answer_search" in prompt_names
        assert "tavily_news_search" in prompt_names
        
        # Check that each prompt has a description and required arguments
        for prompt in prompts:
            assert prompt.description
            assert any(arg.name == "query" and arg.required for arg in prompt.arguments)


@pytest.mark.asyncio
class TestServerCallTool:
    async def test_call_tool_web_search(self, mock_tavily_client, mock_server, web_search_response):
        """Test that the call_tool handler correctly calls the Tavily client for web search."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = web_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function with web search parameters
        result = await call_tool_handler(
            name="tavily_web_search", 
            arguments={
                "query": "test query",
                "max_results": 5,
                "search_depth": "basic",
                "include_domains": ["example.com"],
                "exclude_domains": ["spam.com"]
            }
        )
        
        # Verify the client was called with correct parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            search_depth="basic",
            include_domains=["example.com"],
            exclude_domains=["spam.com"]
        )
        
        # Verify the result is a list of TextContent
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "Detailed Results:" in result[0].text
    
    async def test_call_tool_answer_search(self, mock_tavily_client, mock_server, answer_search_response):
        """Test that the call_tool handler correctly calls the Tavily client for answer search."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = answer_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function with answer search parameters
        result = await call_tool_handler(
            name="tavily_answer_search", 
            arguments={
                "query": "test query",
                "max_results": 5,
                "search_depth": "advanced"
            }
        )
        
        # Verify the client was called with correct parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_domains=[],
            exclude_domains=[]
        )
        
        # Verify the result includes the answer
        assert isinstance(result, list)
        assert "Answer:" in result[0].text
    
    async def test_call_tool_news_search(self, mock_tavily_client, mock_server, news_search_response):
        """Test that the call_tool handler correctly calls the Tavily client for news search."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = news_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function with news search parameters
        result = await call_tool_handler(
            name="tavily_news_search", 
            arguments={
                "query": "test query",
                "max_results": 5,
                "days": 7
            }
        )
        
        # Verify the client was called with correct parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            topic="news",
            days=7,
            include_domains=[],
            exclude_domains=[]
        )
        
        # Verify the result includes published dates
        assert isinstance(result, list)
        assert "Published:" in result[0].text
    
    async def test_call_tool_news_search_default_days(self, mock_tavily_client, mock_server, news_search_response):
        """Test that the news search uses default days value when not specified."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = news_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function with news search parameters, without days
        result = await call_tool_handler(
            name="tavily_news_search", 
            arguments={
                "query": "test query"
            }
        )
        
        # Verify days defaults to 3
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            topic="news",
            days=3,
            include_domains=[],
            exclude_domains=[]
        )
    
    async def test_call_tool_invalid_tool(self, mock_server):
        """Test that call_tool raises an error for an invalid tool name."""
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call with an invalid tool name should raise McpError with INVALID_PARAMS
        with pytest.raises(McpError) as exc_info:
            await call_tool_handler(name="invalid_tool", arguments={"query": "test"})
        assert exc_info.value.error.code == INVALID_PARAMS
        assert "Unknown tool" in str(exc_info.value)
    
    async def test_call_tool_api_key_error(self, mock_tavily_client, mock_server):
        """Test that call_tool handles API key errors correctly."""
        # Set up the mock client to raise an API key error
        # Mock API key error (raised by client)
        mock_tavily_client.search.side_effect = InvalidAPIKeyError
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function and expect an McpError
        with pytest.raises(McpError) as exc_info:
            await call_tool_handler(name="tavily_web_search", arguments={"query": "test"})
        # API key errors map to INTERNAL_ERROR
        assert exc_info.value.error.code == INTERNAL_ERROR
    
    async def test_call_tool_usage_limit_error(self, mock_tavily_client, mock_server):
        """Test that call_tool handles usage limit errors correctly."""
        # Set up the mock client to raise a usage limit error
        # Mock usage limit exceeded error
        mock_tavily_client.search.side_effect = UsageLimitExceededError("Usage limit exceeded")
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function and expect an McpError
        with pytest.raises(McpError) as exc_info:
            await call_tool_handler(name="tavily_web_search", arguments={"query": "test"})
        # Usage limit errors map to INTERNAL_ERROR
        assert exc_info.value.error.code == INTERNAL_ERROR
        
    async def test_call_tool_validation_error(self, mock_server):
        """Test that call_tool properly validates input parameters."""
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Test with invalid max_results
        with pytest.raises(McpError) as exc_info:
            await call_tool_handler(
                name="tavily_web_search", 
                arguments={"query": "test", "max_results": 25}  # Too large
            )
        assert "max_results" in str(exc_info.value).lower()
        
        # Test with invalid search_depth
        with pytest.raises(McpError) as exc_info:
            await call_tool_handler(
                name="tavily_web_search", 
                arguments={"query": "test", "search_depth": "ultra"}  # Invalid option
            )
        assert "search_depth" in str(exc_info.value).lower()
        
        # Test with invalid days for news search
        with pytest.raises(McpError) as exc_info:
            await call_tool_handler(
                name="tavily_news_search", 
                arguments={"query": "test", "days": 400}  # Too large
            )
        assert "days" in str(exc_info.value).lower()
        
    async def test_call_tool_json_domain_input(self, mock_tavily_client, mock_server, web_search_response):
        """Test that call_tool properly handles JSON format for domain lists."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = web_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.call_tool()
        call_tool_handler = mock_server.handler_registry['call_tool']
        
        # Call the function with JSON formatted domain lists
        await call_tool_handler(
            name="tavily_web_search", 
            arguments={
                "query": "test query",
                "include_domains": '["example.com", "test.org"]',
                "exclude_domains": '["spam.com"]'
            }
        )
        
        # Verify the client was called with correct parsed parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            search_depth="basic",
            include_domains=["example.com", "test.org"],
            exclude_domains=["spam.com"]
        )


@pytest.mark.asyncio
class TestServerGetPrompt:
    async def test_get_prompt_web_search(self, mock_tavily_client, mock_server, web_search_response):
        """Test that the get_prompt handler correctly calls the Tavily client for web search."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = web_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function with web search parameters
        result = await get_prompt_handler(
            name="tavily_web_search", 
            arguments={
                "query": "test query",
                "include_domains": "example.com",
                "exclude_domains": "spam.com"
            }
        )
        
        # Verify the client was called with correct parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            include_domains=["example.com"],
            exclude_domains=["spam.com"]
        )
        
        # Verify the result is a GetPromptResult
        assert isinstance(result, GetPromptResult)
        assert "test query" in result.description
        assert len(result.messages) == 1
        assert result.messages[0].role == "user"
        assert isinstance(result.messages[0].content, TextContent)
        assert result.messages[0].content.type == "text"
        
    async def test_get_prompt_answer_search(self, mock_tavily_client, mock_server, answer_search_response):
        """Test that the get_prompt handler correctly calls the Tavily client for answer search."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = answer_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function with answer search parameters
        result = await get_prompt_handler(
            name="tavily_answer_search", 
            arguments={
                "query": "test question",
                "include_domains": "example.com,test.org",
                "exclude_domains": "spam.com"
            }
        )
        
        # Verify the client was called with correct parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test question",
            include_answer=True,
            search_depth="advanced",
            include_domains=["example.com", "test.org"],
            exclude_domains=["spam.com"]
        )
        
        # Verify the result is a GetPromptResult with answer content
        assert isinstance(result, GetPromptResult)
        assert "test question" in result.description
        assert "This is a sample answer" in result.messages[0].content.text
        
    async def test_get_prompt_news_search(self, mock_tavily_client, mock_server, news_search_response):
        """Test that the get_prompt handler correctly calls the Tavily client for news search."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = news_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function with news search parameters including days
        result = await get_prompt_handler(
            name="tavily_news_search", 
            arguments={
                "query": "breaking news",
                "days": "5",
                "include_domains": "reuters.com,bbc.com"
            }
        )
        
        # Verify the client was called with correct parameters
        mock_tavily_client.search.assert_called_once_with(
            query="breaking news",
            topic="news",
            days=5,
            include_domains=["reuters.com", "bbc.com"],
            exclude_domains=[]
        )
        
        # Verify the result contains news-specific elements
        assert isinstance(result, GetPromptResult)
        assert "breaking news" in result.description
        assert "Published:" in result.messages[0].content.text
        
    async def test_get_prompt_news_search_default_days(self, mock_tavily_client, mock_server, news_search_response):
        """Test that the news search uses default days value when not specified in get_prompt."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = news_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function without days parameter
        result = await get_prompt_handler(
            name="tavily_news_search", 
            arguments={
                "query": "breaking news"
            }
        )
        
        # Verify days defaults to 3
        mock_tavily_client.search.assert_called_once_with(
            query="breaking news",
            topic="news",
            days=3,
            include_domains=[],
            exclude_domains=[]
        )
    
    async def test_get_prompt_missing_query(self, mock_server):
        """Test that get_prompt raises an error when query is missing."""
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call with missing query
        with pytest.raises(McpError, match="Query is required"):
            await get_prompt_handler(name="tavily_web_search", arguments={})
        
        # Call with None arguments
        with pytest.raises(McpError, match="Query is required"):
            await get_prompt_handler(name="tavily_web_search", arguments=None)
    
    async def test_get_prompt_invalid_prompt(self, mock_server):
        """Test that get_prompt raises an error for an invalid prompt name."""
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call with an invalid prompt name should raise McpError INVALID_PARAMS
        with pytest.raises(McpError) as exc_info:
            await get_prompt_handler(name="invalid_prompt", arguments={"query": "test"})
        assert exc_info.value.error.code == INVALID_PARAMS
        assert "Unknown prompt" in str(exc_info.value)
    
    async def test_get_prompt_api_error(self, mock_tavily_client, mock_server):
        """Test that get_prompt handles API errors gracefully."""
        # Set up the mock client to raise an API key error
        mock_tavily_client.search.side_effect = InvalidAPIKeyError
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function - should return an error message instead of raising
        result = await get_prompt_handler(
            name="tavily_web_search", 
            arguments={"query": "test query"}
        )
        # Verify the result contains the error message
        assert "failed to search" in result.description.lower()
        assert len(result.messages) == 1
        # Default Tavily error message contains 'api key is invalid'
        assert "api key is invalid" in result.messages[0].content.text.lower()
        
    async def test_get_prompt_usage_limit_error(self, mock_tavily_client, mock_server):
        """Test that get_prompt handles usage limit errors gracefully."""
        # Set up the mock client to raise a usage limit error
        mock_tavily_client.search.side_effect = UsageLimitExceededError("Usage limit exceeded")
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function - should return an error message instead of raising
        result = await get_prompt_handler(
            name="tavily_answer_search", 
            arguments={"query": "test query"}
        )
        # Verify the result contains the error message
        assert "failed to search" in result.description.lower()
        assert "usage limit exceeded" in result.messages[0].content.text.lower()
        
    async def test_get_prompt_json_domain_input(self, mock_tavily_client, mock_server, web_search_response):
        """Test that get_prompt correctly handles JSON domain input."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = web_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function with JSON formatted domain lists
        result = await get_prompt_handler(
            name="tavily_web_search", 
            arguments={
                "query": "test query",
                "include_domains": '["example.com", "test.org"]',
                "exclude_domains": '["spam.com"]'
            }
        )
        
        # Verify the client was called with correct parsed parameters
        mock_tavily_client.search.assert_called_once_with(
            query="test query",
            include_domains=["example.com", "test.org"],
            exclude_domains=["spam.com"]
        )
        
    async def test_get_prompt_string_to_int_conversion(self, mock_tavily_client, mock_server, news_search_response):
        """Test that get_prompt correctly converts string days parameter to int."""
        # Set up the mock client to return our test response
        mock_tavily_client.search.return_value = news_search_response
        
        # Create a server instance to get the decorated function
        await server_module.serve("fake_api_key")
        
        # Get the function that was registered with @server.get_prompt()
        get_prompt_handler = mock_server.handler_registry['get_prompt']
        
        # Call the function with days as string
        await get_prompt_handler(
            name="tavily_news_search", 
            arguments={
                "query": "news",
                "days": "7"  # String instead of int
            }
        )
        
        # Verify the client was called with days converted to int
        mock_tavily_client.search.assert_called_once_with(
            query="news",
            topic="news",
            days=7,  # Should be converted to int
            include_domains=[],
            exclude_domains=[]
        )