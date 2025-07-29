"""Configuration management using pydantic."""

import os
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    
    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(2, ge=1, le=20, description="Connection pool size")
    max_overflow: int = Field(3, ge=0, le=30, description="Maximum overflow connections")
    pool_timeout: int = Field(30, ge=5, le=300, description="Pool timeout in seconds")
    pool_recycle: int = Field(1800, ge=300, le=7200, description="Connection recycle time in seconds")
    connect_timeout: int = Field(10, ge=1, le=60, description="Connection timeout in seconds")
    statement_timeout: int = Field(30000, ge=1000, le=300000, description="Statement timeout in milliseconds")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Convert postgres:// to postgresql:// for compatibility."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    @property
    def is_postgresql(self) -> bool:
        """Check if database is PostgreSQL."""
        return self.url.startswith("postgresql://")


class QueryConfig(BaseModel):
    """Query execution configuration."""
    
    default_timeout: int = Field(30, ge=1, le=300, description="Default query timeout in seconds")
    default_max_rows: int = Field(100, ge=0, le=10000, description="Default max rows to return")
    max_sample_size: int = Field(100, ge=1, le=1000, description="Maximum sample size for table exploration")


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # Database settings
    database_url: str = Field(default="")
    
    # Query settings
    default_timeout: int = Field(default=30)
    default_max_rows: int = Field(default=100)
    max_sample_size: int = Field(default=100)
    
    # Pool settings
    pool_size: int = Field(default=2)
    max_overflow: int = Field(default=3)
    pool_recycle: int = Field(default=1800)
    
    # Logging
    log_level: str = Field(default="INFO")
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        if not self.database_url:
            # Allow missing DATABASE_URL during testing
            if "pytest" in os.sys.modules:
                self.database_url = "sqlite:///test.db"
            else:
                raise ValueError("DATABASE_URL environment variable is required")
        
        return DatabaseConfig(
            url=self.database_url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_recycle=self.pool_recycle,
        )
    
    def get_query_config(self) -> QueryConfig:
        """Get query configuration."""
        return QueryConfig(
            default_timeout=self.default_timeout,
            default_max_rows=self.default_max_rows,
            max_sample_size=self.max_sample_size,
        )