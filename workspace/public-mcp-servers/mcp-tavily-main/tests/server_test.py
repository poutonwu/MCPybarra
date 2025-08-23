#!/usr/bin/env python
"""
Test script to check if the server module can be instantiated.
This is a minimal test that doesn't start an actual server.
"""

import sys
import asyncio
from mcp_server_tavily.server import Server
from unittest.mock import MagicMock


async def test_server():
    """Test if the server can be instantiated."""
    print(f"Testing with Python {sys.version}")
    
    print("Creating server instance...")
    server = Server("mcp-tavily-test")
    
    # Set up mock handler for list_tools
    tools_called = False
    
    @server.list_tools()
    async def list_tools():
        nonlocal tools_called
        tools_called = True
        return []
    
    print("✓ Server created and decorator registered")
    print("\n✅ Server initialization test passed!")


if __name__ == "__main__":
    asyncio.run(test_server())