"""
Kolektor MCP Server - Secure IFC Processing for Claude Desktop

This is the main entry point for the MCP server. All processing logic
is implemented in compiled Cython modules for security and performance.
"""

from fastmcp import FastMCP
from .tools import register_tools

# Initialize the MCP server with our application name
mcp = FastMCP("Kolektor IFC Processor")


def main():
    """Main entry point for the MCP server."""
    # Register all IFC processing tools
    register_tools(mcp)
    
    # Start the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
