#!/usr/bin/env python3
"""MCP server providing database exploration and query tools."""

import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .exceptions import (
    DatabaseToolsError,
    QueryExecutionError,
    QueryTimeoutError,
    QueryValidationError,
    TableNotFoundError,
)
from .query_builder import QueryValidator
from .repository import DatabaseRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Set log level from settings
logging.getLogger().setLevel(settings.log_level)

# Initialize MCP application
app = FastMCP("database-tools")

# Initialize repository
db_config = settings.get_database_config()
query_config = settings.get_query_config()
repository = DatabaseRepository(db_config)


def format_langflow_error(error: Exception) -> Dict[str, Any]:
    """
    Format error for Langflow compatibility.
    
    list_tables and explore_table return simple {"error": str}
    query_database returns full error object
    """
    if isinstance(error, DatabaseToolsError):
        return {"error": error.message}
    return {"error": str(error)}


def format_query_error(error: Exception) -> Dict[str, Any]:
    """Format error for query_database with full details."""
    error_message = str(error)
    
    # Clean up SQL details from error message
    if '\n[SQL' in error_message:
        error_message = error_message.split('\n[SQL')[0].strip()
    
    # Truncate long error messages
    if len(error_message) > 300:
        error_message = error_message[:300] + "..."
    
    # Determine error type and recommendation
    if isinstance(error, QueryValidationError):
        return {
            "error": error_message,
            "error_type": "ValidationError",
            "recommendation": "Only SELECT and WITH queries are allowed for security"
        }
    elif isinstance(error, QueryTimeoutError):
        return {
            "error": error_message,
            "error_type": "TimeoutError",
            "recommendation": "Try a simpler query or increase the timeout"
        }
    elif isinstance(error, QueryExecutionError):
        return {
            "error": error_message,
            "error_type": "QueryExecutionError",
            "recommendation": "Review query syntax and table structure"
        }
    else:
        return {
            "error": error_message,
            "error_type": type(error).__name__,
            "recommendation": "Use list_tables and explore_table to understand the database structure"
        }


@app.tool()
def list_tables(include_views: bool = True) -> str:
    """
    Get list of tables and optionally views in the database.
    """
    start_time = time.time()
    
    try:
        tables = repository.get_tables()
        views = repository.get_views() if include_views else []
        
        response = {
            "tables": tables,
            "views": views,
            "total_tables": len(tables),
            "total_views": len(views),
            "database_type": repository.get_database_type()
        }
        
        execution_time = time.time() - start_time
        logger.info(f"Found {len(tables)} tables and {len(views)} views in {execution_time:.3f}s")
        return json.dumps(response, indent=2)
        
    except Exception as e:
        logger.exception(f"Error retrieving table list after {time.time() - start_time:.3f}s")
        return json.dumps(format_langflow_error(e), indent=2)


@app.tool()
def explore_table(table_name: str, sample_size: int = 3) -> str:
    """
    Get table structure and sample data.
    """
    if not table_name or not table_name.strip():
        return json.dumps({"error": "Table name is required"}, indent=2)
    
    start_time = time.time()
    sample_size = min(query_config.max_sample_size, max(0, sample_size))
    
    try:
        # Get table metadata
        columns = repository.get_table_columns(table_name)
        primary_key = repository.get_primary_keys(table_name)
        foreign_keys = repository.get_foreign_keys(table_name)
        row_count = repository.get_row_count(table_name)
        sample_data = repository.get_sample_data(table_name, sample_size)
        
        response = {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "sample_data": sample_data
        }
        
        execution_time = time.time() - start_time
        logger.info(f"Table '{table_name}' analyzed successfully in {execution_time:.3f}s")
        return json.dumps(response, indent=2)
        
    except TableNotFoundError:
        return json.dumps({"error": f"Table '{table_name}' not found"}, indent=2)
    except Exception as e:
        execution_time = time.time() - start_time
        logger.exception(f"Error analyzing table after {execution_time:.3f}s")
        return json.dumps(format_langflow_error(e), indent=2)


@app.tool()
def query_database_readonly(
    query: str,
    timeout_seconds: int = None,
    max_rows: int = None
) -> str:
    """
    Execute read-only SELECT query with safety features.
    
    Only supports SELECT queries and WITH clauses. Other operations
    (INSERT, UPDATE, DELETE, etc.) are blocked for safety.
    """
    # Use defaults from config if not provided
    if timeout_seconds is None:
        timeout_seconds = query_config.default_timeout
    if max_rows is None:
        max_rows = query_config.default_max_rows
    
    if not query or not query.strip():
        return json.dumps({
            "error": "Query parameter is required and cannot be empty",
            "error_type": "ValidationError",
            "recommendation": "Provide a valid SQL SELECT query"
        }, indent=2)
    
    # Validate query
    try:
        QueryValidator.validate(query)
    except QueryValidationError as e:
        return json.dumps(format_query_error(e), indent=2)
    
    start_time = time.time()
    
    try:
        # Execute with timeout using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                repository.execute_query,
                query,
                timeout_seconds
            )
            
            try:
                results, columns = future.result(timeout=timeout_seconds)
                execution_time = time.time() - start_time
            except FutureTimeoutError:
                raise QueryTimeoutError(timeout_seconds)
        
        # Apply row limit
        if max_rows > 0 and len(results) > max_rows:
            results = results[:max_rows]
        
        response = {
            "result": results,
            "row_count": len(results),
            "columns": columns,
            "execution_time": round(execution_time, 3)
        }
        
        logger.info(f"Query executed in {execution_time:.3f}s, returned {len(results)} rows")
        return json.dumps(response, indent=2)
        
    except Exception as e:
        logger.exception("Query execution error")
        return json.dumps(format_query_error(e), indent=2)


def main():
    """Main entry point."""
    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.exception("Unexpected error")
        sys.exit(1)
    finally:
        repository.close()


if __name__ == "__main__":
    main()