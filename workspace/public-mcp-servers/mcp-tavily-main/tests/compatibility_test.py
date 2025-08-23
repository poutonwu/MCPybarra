#!/usr/bin/env python
"""
Basic compatibility test for MCP Tavily.
This script verifies that the package can be imported and basic classes can be instantiated.
"""

import sys
import importlib
import asyncio


def run_compatibility_test():
    """Run basic compatibility tests to verify the package works."""
    print(f"Testing with Python {sys.version}")
    
    # Test importing the package
    print("Testing imports...")
    import mcp_server_tavily
    from mcp_server_tavily.server import SearchBase, GeneralSearch, AnswerSearch, NewsSearch
    print("✓ Imports successful")
    
    # Test basic class instantiation
    print("Testing model instantiation...")
    test_model = SearchBase(query="test query")
    assert test_model.query == "test query"
    assert test_model.max_results == 5
    
    # Test domain parsing
    domains = SearchBase.parse_domains_list("example.com,test.org")
    assert domains == ["example.com", "test.org"]
    print("✓ Models working correctly")
    
    # Print successful result
    print("\n✅ Compatibility test passed!")


if __name__ == "__main__":
    run_compatibility_test()