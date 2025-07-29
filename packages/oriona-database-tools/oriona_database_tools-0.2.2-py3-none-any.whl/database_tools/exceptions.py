"""Custom exceptions for database tools."""

from typing import Optional


class DatabaseToolsError(Exception):
    """Base exception for all database tools errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConnectionError(DatabaseToolsError):
    """Raised when database connection fails."""
    pass


class ValidationError(DatabaseToolsError):
    """Raised when input validation fails."""
    pass


class QueryValidationError(ValidationError):
    """Raised when SQL query validation fails."""
    pass


class TableNotFoundError(DatabaseToolsError):
    """Raised when a table doesn't exist."""
    
    def __init__(self, table_name: str):
        super().__init__(f"Table '{table_name}' not found")
        self.table_name = table_name


class QueryExecutionError(DatabaseToolsError):
    """Raised when query execution fails."""
    pass


class QueryTimeoutError(QueryExecutionError):
    """Raised when query exceeds timeout."""
    
    def __init__(self, timeout_seconds: int):
        super().__init__(f"Query execution exceeded {timeout_seconds} seconds timeout")
        self.timeout_seconds = timeout_seconds


class ConfigurationError(DatabaseToolsError):
    """Raised when configuration is invalid."""
    pass