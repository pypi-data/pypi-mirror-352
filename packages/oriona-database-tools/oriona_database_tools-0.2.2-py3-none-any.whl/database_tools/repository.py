"""Repository pattern for database operations."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, Inspector
from sqlalchemy.pool import QueuePool

from .config import DatabaseConfig
from .exceptions import ConnectionError, TableNotFoundError
from .query_builder import QueryBuilder

logger = logging.getLogger(__name__)


class DatabaseRepository:
    """Repository for database operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize repository with configuration."""
        self.config = config
        self._engine: Optional[Engine] = None
        self._inspector: Optional[Inspector] = None
    
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.config.url,
                    poolclass=QueuePool,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    pool_pre_ping=True,
                    pool_recycle=self.config.pool_recycle,
                    connect_args=self._get_connect_args()
                )
                logger.info("Created database connection pool")
            except Exception as e:
                raise ConnectionError(f"Failed to create database engine: {str(e)}")
        return self._engine
    
    @property
    def inspector(self) -> Inspector:
        """Get or create database inspector."""
        if self._inspector is None:
            self._inspector = inspect(self.engine)
        return self._inspector
    
    def _get_connect_args(self) -> dict:
        """Get database-specific connection arguments."""
        if self.config.is_postgresql:
            return {
                "connect_timeout": self.config.connect_timeout,
                "options": f"-c statement_timeout={self.config.statement_timeout}"
            }
        return {}
    
    def get_tables(self) -> List[str]:
        """Get list of table names."""
        try:
            return self.inspector.get_table_names()
        except Exception as e:
            raise ConnectionError(f"Failed to retrieve tables: {str(e)}")
    
    def get_views(self) -> List[str]:
        """Get list of view names."""
        try:
            return self.inspector.get_view_names()
        except Exception as e:
            raise ConnectionError(f"Failed to retrieve views: {str(e)}")
    
    def get_database_type(self) -> str:
        """Get database dialect name."""
        return self.engine.dialect.name
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table or view exists."""
        all_tables = self.get_tables() + self.get_views()
        return table_name in all_tables
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        columns = []
        for col in self.inspector.get_columns(table_name):
            columns.append({
                "name": col['name'],
                "type": str(col['type']),
                "nullable": col.get('nullable', True),
                "default": str(col.get('default', '')) if col.get('default') else None,
            })
        return columns
    
    def get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns for a table."""
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        return pk_constraint.get('constrained_columns', []) if pk_constraint else []
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "columns": fk['constrained_columns'],
                "references": QueryBuilder.format_foreign_key_reference(
                    fk['referred_table'], 
                    fk['referred_columns']
                )
            })
        return foreign_keys
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for a table."""
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        query = QueryBuilder.count_query(table_name)
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.scalar()
    
    def get_sample_data(self, table_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        if limit <= 0:
            return []
        
        query, params = QueryBuilder.sample_query(table_name, limit)
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            columns = list(result.keys())
            
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert non-primitive types to string
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    row_dict[col] = value
                rows.append(row_dict)
            
            return rows
    
    def execute_query(self, query: str, timeout: int) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Execute a query with timeout.
        
        Args:
            query: SQL query to execute
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (results, column_names)
        """
        with self.engine.connect() as conn:
            # Set statement timeout for PostgreSQL
            if self.config.is_postgresql:
                conn.execute(text(f"SET LOCAL statement_timeout = {timeout * 1000}"))
            
            result = conn.execute(text(query))
            columns = list(result.keys())
            
            # Convert results to list of dicts
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    row_dict[col] = value
                rows.append(row_dict)
            
            return rows, columns
    
    def close(self):
        """Close database connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._inspector = None