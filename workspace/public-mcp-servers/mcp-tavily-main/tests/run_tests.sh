#!/bin/bash
set -e

# Ensure we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo "Error: Virtual environment not found. Please create it first."
        exit 1
    fi
fi

# Install test dependencies
echo "Installing test dependencies..."
if command -v uv &> /dev/null; then
    # Use uv if available
    uv sync --dev
    uv pip install -e .
else
    # Fall back to pip
    pip install -r requirements-dev.txt
    pip install -e .
fi

# Run all tests with coverage and suppress warnings
echo "Running all tests with coverage..."
python -W ignore -m pytest tests --cov=src/mcp_server_tavily --cov-report=term

echo "Tests complete!"