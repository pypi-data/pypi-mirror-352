"""SQL query builder and validator."""

from typing import List, Tuple

import sqlparse
from sqlparse.sql import Comment

from .exceptions import QueryValidationError


class QueryValidator:
    """Validates SQL queries for safety."""
    
    DANGEROUS_KEYWORDS = frozenset([
        'DROP', 'TRUNCATE', 'DELETE', 'INSERT', 'UPDATE',
        'ALTER', 'CREATE', 'GRANT', 'REVOKE'
    ])
    
    ALLOWED_STATEMENT_TYPES = {'SELECT', 'UNKNOWN'}  # UNKNOWN for WITH queries
    
    @classmethod
    def validate(cls, query: str) -> None:
        """
        Validate that a query is safe to execute.
        
        Args:
            query: SQL query to validate
            
        Raises:
            QueryValidationError: If query is invalid or unsafe
        """
        if not query or not query.strip():
            raise QueryValidationError("Query cannot be empty")
        
        try:
            parsed = sqlparse.parse(query)
            if not parsed:
                raise QueryValidationError("Unable to parse SQL query")
            
            # Check for multiple statements
            if len(parsed) > 1:
                raise QueryValidationError("Multiple statements are not allowed")
            
            statement = parsed[0]
            stmt_type = statement.get_type()
            
            # Check statement type
            if stmt_type not in cls.ALLOWED_STATEMENT_TYPES:
                raise QueryValidationError("Only SELECT queries are allowed")
            
            # For UNKNOWN type, check if it's a WITH statement
            if stmt_type == 'UNKNOWN':
                if not cls._is_with_query(statement):
                    raise QueryValidationError("Only SELECT queries are allowed")
            
            # Check for dangerous keywords
            cls._check_dangerous_keywords(statement)
            
        except QueryValidationError:
            raise
        except Exception as e:
            raise QueryValidationError(f"Query validation error: {str(e)}")
    
    @classmethod
    def _is_with_query(cls, statement) -> bool:
        """Check if an UNKNOWN statement is a WITH query."""
        for token in statement.tokens:
            if not token.is_whitespace and not isinstance(token, Comment):
                if token.ttype in (sqlparse.tokens.Keyword, sqlparse.tokens.Keyword.CTE):
                    return str(token).upper() == 'WITH'
                # If we hit a non-keyword token first, it's not a valid query
                return False
        return False
    
    @classmethod
    def _check_dangerous_keywords(cls, statement) -> None:
        """Check for dangerous keywords in the statement."""
        for token in statement.flatten():
            if (token.ttype in (sqlparse.tokens.Keyword, 
                               sqlparse.tokens.Keyword.DDL, 
                               sqlparse.tokens.Keyword.DML) and
                str(token).upper() in cls.DANGEROUS_KEYWORDS):
                raise QueryValidationError(f"Dangerous keyword '{token}' detected")


class QueryBuilder:
    """Builds safe SQL queries."""
    
    @staticmethod
    def count_query(table_name: str) -> str:
        """
        Build a count query for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            SQL query string
        """
        # Using f-string here is safe as this is internal
        # In production, consider using SQLAlchemy's table reflection
        return f"SELECT COUNT(*) FROM {table_name}"
    
    @staticmethod
    def sample_query(table_name: str, limit: int) -> Tuple[str, dict]:
        """
        Build a query to get sample data from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows
            
        Returns:
            Tuple of (query, parameters)
        """
        # Return parameterized query
        return f"SELECT * FROM {table_name} LIMIT :limit", {"limit": limit}
    
    @staticmethod
    def format_foreign_key_reference(table: str, columns: List[str]) -> str:
        """
        Format foreign key reference string.
        
        Args:
            table: Referenced table name
            columns: Referenced column names
            
        Returns:
            Formatted reference string
        """
        return f"{table}.{columns}"