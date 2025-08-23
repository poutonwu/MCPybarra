"""
Main entry point for the Word Document MCP Server.
Acts as the central controller for the MCP server that handles Word document operations.
"""

import os
import sys
from mcp.server.fastmcp import FastMCP
from word_document_server.tools import (
    document_tools,
    content_tools,
    format_tools,
    protection_tools,
    footnote_tools,
    extended_document_tools
)



# Initialize FastMCP server
mcp = FastMCP("word-document-server")

def register_tools():
    """Register all tools with the MCP server."""
    # Document tools (create, copy, info, etc.)
    mcp.tool()(document_tools.create_document)
    mcp.tool()(document_tools.get_document_text)
    
    # Content tools (paragraphs, headings, tables, etc.)
    mcp.tool()(content_tools.add_paragraph)
    mcp.tool()(content_tools.add_heading)
    
    # Format tools (styling, text formatting, etc.)
    mcp.tool()(format_tools.create_custom_style)
    mcp.tool()(format_tools.format_text)
    
    # Protection tools
    mcp.tool()(protection_tools.protect_document)
    
    # Footnote tools
    mcp.tool()(footnote_tools.add_footnote_to_document)
    
    # Extended document tools
    mcp.tool()(extended_document_tools.get_paragraph_text_from_document)
    mcp.tool()(extended_document_tools.find_text_in_document)


def run_server():
    """Run the Word Document MCP Server."""
    # Register all tools
    register_tools()
    
    # Run the server
    mcp.run(transport='stdio')
    return mcp

if __name__ == "__main__":
    run_server()
