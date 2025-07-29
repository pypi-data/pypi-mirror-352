"""
MCP server implementation for the Dynamics 365 Table Relationship Finder.
"""
import argparse
import sys
from fastmcp import FastMCP
from .config import DEFAULT_RELATIONSHIP_FILE
from .tools import *

def create_server(relationship_file=None):
    """
    Create and configure the MCP server.
    
    Args:
        relationship_file (str, optional): Path to the relationship file
        
    Returns:
        FastMCP: The configured MCP server
    """
    
    # If relationship file is provided, update the default
    if relationship_file:
        from .config import DEFAULT_RELATIONSHIP_FILE
        DEFAULT_RELATIONSHIP_FILE = relationship_file
    
    # Initialize the MCP server
    mcp = FastMCP(
        name="Dynamics 365 Table Relationship Explorer",
        description="MCP server for finding relationships between Dynamics 365 tables",
    )
    
    # Register tools directly from functions
    mcp.add_tool(find_related_tables)
    mcp.add_tool(find_relationship_path)
    mcp.add_tool(get_relationship_details)
    mcp.add_tool(list_tables)
    mcp.add_tool(get_stats)
    # mcp.add_tool(tools.optimize_relationship_file)
    
    return mcp

def main():
    """CLI entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Start the Dynamics 365 Table Relationship Finder MCP server")
    parser.add_argument(
        "--relationship-file",
        "-r", 
        default=DEFAULT_RELATIONSHIP_FILE, 
        help=f"Path to the relationship file (default: {DEFAULT_RELATIONSHIP_FILE})"
    )
    
    args = parser.parse_args()
    
    # Create the server with the specified relationship file
    mcp = create_server(args.relationship_file)
    
    # Start the server
    print(f"Starting MCP server with relationship file: {args.relationship_file}")
    print("Server starting...")
    mcp.run()

if __name__ == "__main__":
    main() 