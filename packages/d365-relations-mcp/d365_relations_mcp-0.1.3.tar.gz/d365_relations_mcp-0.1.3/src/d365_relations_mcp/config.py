"""
Configuration module for the Dynamics 365 Table Relationship Finder MCP server.
"""
import os

# Default relationship file path - can be overridden via environment variable or CLI arg
DEFAULT_RELATIONSHIP_FILE = os.environ.get(
    "D365_RELATIONSHIP_FILE", 
    "tablefieldassociations_opt.json"
) 