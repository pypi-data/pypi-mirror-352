# Dynamics 365 Table Relationship Finder MCP Server

An MCP (Model Context Protocol) server for the Dynamics 365 Table Relationship Finder, enabling AI assistants to find and understand relationships between Dynamics 365 tables.

## Features

- **MCP Integration**: Expose table relationship finder functionality through the standardized MCP protocol
- **AI Assistant Ready**: Designed to be integrated with AI assistants like Claude and GPT

## Installation

This package requires the core `dynamics365-relationship-finder` package.

```bash
# Install the MCP package
pip install dynamics365-relationship-finder-mcp
```

## Usage

### With Cursor

Add the following to the list of MCP-servers in `mcp.json` in cursor
```json
"d365-relations-mcp": {
  "command": "uv",
  "args": [
    "--directory",
    "path/to/package",
    "run",
    "mcp"
  ]
}
```

### Alternatively manually running the MCP Server

```bash
# Start with default settings
uv run mcp

# Specify a custom relationship file
uv run mcp --relationship-file my_custom_relationships.json
```

You can also set the relationship file path via an environment variable:

```bash
export D365_RELATIONSHIP_FILE=my_custom_relationships.json
dynamics365-mcp
```

### Available MCP Tools

The MCP server exposes the following tools:

1. **find_related_tables**
   - Purpose: Find all tables directly related to a specific table.
   - Parameters:
     - `table` (string): Name of the table to find relationships for (case-insensitive).
     - `relationship_file` (string, optional): Path to the relationship file.

2. **find_relationship_path**
   - Purpose: Find paths between two tables through their relationships.
   - Parameters:
     - `table1` (string): Name of the first table (case-insensitive).
     - `table2` (string): Name of the second table (case-insensitive).
     - `levels` (integer, optional, default=0): Maximum number of intermediate tables to check.
     - `relationship_file` (string, optional): Path to the relationship file.

3. **get_relationship_details**
   - Purpose: Get detailed information about the direct relationship between two tables.
   - Parameters:
     - `table1` (string): Name of the first table (case-insensitive).
     - `table2` (string): Name of the second table (case-insensitive).
     - `relationship_file` (string, optional): Path to the relationship file.

4. **list_tables**
   - Purpose: List all tables in the dataset.
   - Parameters:
     - `relationship_file` (string, optional): Path to the relationship file.

5. **get_stats**
   - Purpose: Get statistics about the loaded relationships.
   - Parameters:
     - `relationship_file` (string, optional): Path to the relationship file.

## Example Client Usage

Using the FastMCP client:

```python
from fastmcp.client import MCPClient

# Connect to the MCP server
client = MCPClient()

# Get all tables related to Customer
related_tables = client.call("find_related_tables", {"table": "Customer"})
print(related_tables)

# Find relationship path between Customer and SalesOrder
paths = client.call("find_relationship_path", {
    "table1": "Customer", 
    "table2": "SalesOrder", 
    "levels": 2
})
print(paths)
```

## Example AI Assistant Prompts

When using with AI assistants, you can provide prompts like:

```
You have access to a Dynamics 365 Table Relationship Finder through MCP tools. 
You can use these tools to find relationships between tables and understand the data model.

Example tasks:
1. Find all tables directly related to the Custtrans table
2. Find a path between Customer and SalesOrderLine tables
3. Show me the details of how Customer and SalesOrder are related
4. List all tables in the system
5. Show me statistics about the relationships
```

## License

MIT 