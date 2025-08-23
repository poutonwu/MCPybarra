# Tests for MCP Tavily

This directory contains tests for the MCP Tavily server, which provides web search functionality via the Tavily API.

## Test Structure

- `test_models.py` - Tests for the data models and validation
- `test_utils.py` - Tests for utility functions like `format_results`
- `test_server_api.py` - Tests for server API handlers (list_tools, call_tool, etc.)
- `test_integration.py` - Integration tests for the server as a whole

## Running Tests

Make sure your virtual environment is activated, then run:

```bash
./tests/run_tests.sh
```

This will:
1. Install test dependencies using `uv`
2. Run tests with coverage reporting
3. Generate a coverage report in the `htmlcov` directory

## Test Coverage

The tests cover:
- Data model validation and parameter validation
- Parameter parsing (especially domain lists)
- Utility functions for formatting results
- Command-line interface
- Error handling (API errors, validation errors)
- Domain filtering functionality
- String-to-int conversion of numeric parameters
- JSON input formats

Current test coverage is around 46%, focusing on the most critical parts of the API functionality. The remaining uncovered areas mostly involve the stdio server interaction and parts of the main server loop, which depend on the MCP framework's components.