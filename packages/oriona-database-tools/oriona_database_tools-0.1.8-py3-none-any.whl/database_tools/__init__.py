"""Database tools MCP server package."""

from .exceptions import (
    ConnectionError,
    DatabaseToolsError,
    QueryExecutionError,
    QueryTimeoutError,
    QueryValidationError,
    TableNotFoundError,
    ValidationError,
)
from .query_builder import QueryBuilder, QueryValidator
from .repository import DatabaseRepository

__all__ = [
    # Exceptions
    "DatabaseToolsError",
    "ConnectionError",
    "ValidationError",
    "QueryValidationError",
    "TableNotFoundError",
    "QueryExecutionError",
    "QueryTimeoutError",
    # Core classes
    "QueryValidator",
    "QueryBuilder",
    "DatabaseRepository",
]

__version__ = "0.1.0"