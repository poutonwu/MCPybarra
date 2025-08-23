# Contributing to MCP Tavily

Thank you for your interest in contributing to MCP Tavily! This document provides guidelines and instructions for contributing to the project.

## Project Structure

```
mcp-tavily/
├── dist/                  # Distribution files
├── src/
│   └── mcp_server_tavily/ # Source code
│       ├── __init__.py    # Package initialization and CLI
│       ├── __main__.py    # Entry point
│       └── server.py      # Server implementation
├── tests/
│   ├── conftest.py        # Test fixtures
│   ├── helpers.py         # Test helpers
│   ├── test_models.py     # Tests for data models
│   ├── test_utils.py      # Tests for utility functions
│   ├── test_server_api.py # Tests for server API handlers
│   └── test_integration.py # Integration tests
├── .env.sample            # Sample environment variables
├── LICENSE                # MIT License
├── pyproject.toml         # Project configuration
├── README.md              # Project documentation
└── uv.lock                # Dependency lock file
```

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RamXX/mcp-tavily.git
   cd mcp-tavily
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Install development dependencies**:
   ```bash
   uv add --dev pytest pytest-asyncio pytest-mock pytest-cov
   ```

5. **Install the package in development mode**:
   ```bash
   uv pip install -e .
   ```

6. **Set up your Tavily API key**:
   Create a `.env` file in the project root with your Tavily API key:
   ```
   TAVILY_API_KEY=your_api_key_here
   ```

## Testing

### Running Tests

The project includes a test suite that verifies the functionality of various components:

```bash
# Run all tests
./tests/run_tests.sh

# Run specific test files
python -m pytest tests/test_models.py
python -m pytest tests/test_utils.py

# Run with increased verbosity
python -m pytest -v tests/test_models.py
```

### Test Structure

- **Model Tests**: Verify the validation and behavior of data models
- **Utility Tests**: Test formatting and parsing functions
- **API Tests**: Test server API handlers and error handling
- **Integration Tests**: Test the complete server behavior

### Adding New Tests

When adding new features, please include appropriate tests:

1. For new data models, add tests in `tests/test_models.py`
2. For utility functions, add tests in `tests/test_utils.py`
3. For API handlers, add tests in `tests/test_server_api.py`
4. For integration tests, add tests in `tests/test_integration.py`

## Code Style

Please follow these guidelines when contributing:

- Use [Black](https://black.readthedocs.io/en/stable/) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Include docstrings for new functions and classes
- Write clear commit messages that explain the "why" behind changes

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes with descriptive commit messages
6. Push to your feature branch
7. Open a Pull Request against the main repository

## License

By contributing to MCP Tavily, you agree that your contributions will be licensed under the project's MIT License.