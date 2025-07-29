"""
MCP tools for the Dynamics 365 Table Relationship Finder.
"""
from fastmcp import FastMCP
from .config import DEFAULT_RELATIONSHIP_FILE
from d365_relations_cli import AdvancedTableRelationshipFinder
    

def find_related_tables(table: str, relationship_file: str = None) -> dict:
    """
    Find all tables directly related to a specific table.
    
    Args:
        table: Name of the table to find relationships for (case-insensitive).
        relationship_file: Optional path to the relationship file. If not provided, uses the default.
    
    Returns:
        A dictionary mapping related table names to their relationship details.
    """
        
    # Initialize the finder with the appropriate file
    finder = AdvancedTableRelationshipFinder(relationship_file or DEFAULT_RELATIONSHIP_FILE)
    
    # Call the core function
    result = finder.find_related(table)
    
    return result

def find_relationship_path(table1: str, table2: str, levels: int = 0, relationship_file: str = None) -> list:
    """
    Find paths between two tables through their relationships.
    
    Args:
        table1: Name of the first table (case-insensitive).
        table2: Name of the second table (case-insensitive).
        levels: Maximum number of intermediate tables to check. Default is 0 (direct relationships only).
        relationship_file: Optional path to the relationship file. If not provided, uses the default.
    
    Returns:
        A list of paths between the tables, where each path is a list of (table, field, relationship_type) tuples.
    """
        
    # Initialize the finder with the appropriate file
    finder = AdvancedTableRelationshipFinder(relationship_file or DEFAULT_RELATIONSHIP_FILE)
    
    # Call the core function
    result = finder.find_relationship(table1, table2, levels)
    
    # Convert tuples to lists for JSON serialization if needed
    serializable_paths = []
    for path in result:
        serializable_paths.append([{"table": t, "field": f, "relationship_type": rt} for t, f, rt in path])
    
    return serializable_paths

def get_relationship_details(table1: str, table2: str, relationship_file: str = None) -> dict:
    """
    Get detailed information about the direct relationship between two tables.
    
    Args:
        table1: Name of the first table (case-insensitive).
        table2: Name of the second table (case-insensitive).
        relationship_file: Optional path to the relationship file. If not provided, uses the default.
    
    Returns:
        A dictionary with the relationship details or None if no direct relationship exists.
    """
        
    # Initialize the finder with the appropriate file
    finder = AdvancedTableRelationshipFinder(relationship_file or DEFAULT_RELATIONSHIP_FILE)
    
    # Call the core function
    result = finder.get_relationship_details(table1, table2)
    
    return result

def list_tables(relationship_file: str = None) -> list:
    """
    List all tables in the dataset.
    
    Args:
        relationship_file: Optional path to the relationship file. If not provided, uses the default.
    
    Returns:
        A list of all table names.
    """
        
    # Initialize the finder with the appropriate file
    finder = AdvancedTableRelationshipFinder(relationship_file or DEFAULT_RELATIONSHIP_FILE)
    
    # Call the core function
    result = finder.get_table_list()
    
    return result

def get_stats(relationship_file: str = None) -> dict:
    """
    Get statistics about the loaded relationships.
    
    Args:
        relationship_file: Optional path to the relationship file. If not provided, uses the default.
    
    Returns:
        A dictionary with statistics about the relationship data.
    """
        
    # Initialize the finder with the appropriate file
    finder = AdvancedTableRelationshipFinder(relationship_file or DEFAULT_RELATIONSHIP_FILE)
    
    # Call the core function
    result = finder.get_stats()
    
    return result

# def optimize_relationship_file(input_file: str, output_file: str) -> dict:
#     """
#     Create an advanced optimized version of the relationships file.
    
#     Args:
#         input_file: Path to the original JSON file.
#         output_file: Path to save the advanced optimized JSON file.
    
#     Returns:
#         Statistics about the optimization process.
#     """
#     if not CORE_PACKAGE_AVAILABLE:
#         _missing_core_package()
        
#     # Call the core function
#     result = core_optimize(input_file, output_file)
    
#     return result 