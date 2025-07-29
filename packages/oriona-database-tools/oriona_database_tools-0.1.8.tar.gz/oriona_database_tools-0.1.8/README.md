# Database Tools MCP Server

An MCP (Model Context Protocol) server that provides database exploration and query tools for AI assistants. This server enables safe SQL querying and database schema exploration with built-in security features.

## Features

- **Table List Explorer**: List all tables and views in a database
- **Table Details Explorer**: Get detailed schema information and sample data for specific tables
- **Query Engine**: Execute read-only SQL queries with safety features and timeouts

## Installation

No installation required! Use uvx to run directly:

```bash
uvx oriona-database-tools
```

## Quick Start

1. **No installation needed** - uvx runs the package directly

2. **Set your database URL**:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/mydb"
   ```

3. **Add to Claude Desktop** (see configuration below)

## Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "database-tools": {
      "command": "uvx",
      "args": [
        "oriona-database-tools"
      ],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/mydb"
      }
    }
  }
}
```

**Security Note**: Always use a read-only database user for the MCP server to ensure data safety.

## Available Tools

### 1. list_tables

List all tables and views in a database.

**Parameters:**

- `include_views` (boolean, optional): Include database views in the list (default: true)

**Example:**

```json
{
  "tool": "list_tables",
  "arguments": {
    "include_views": true
  }
}
```

### 2. explore_table

Get detailed information about a specific table including schema, foreign keys, and sample data.

**Parameters:**

- `table_name` (string, required): The name of the table to analyze
- `sample_size` (integer, optional): Number of sample rows to retrieve (0-100, default: 3)

**Example:**

```json
{
  "tool": "explore_table",
  "arguments": {
    "table_name": "customers",
    "sample_size": 5
  }
}
```

### 3. query_database

Execute read-only SQL queries with safety features.

**Parameters:**

- `query` (string, required): The SQL query to execute (SELECT only)
- `timeout_seconds` (integer, optional): Maximum query execution time in seconds (default: 30)
- `max_rows` (integer, optional): Maximum number of rows to return (0 for unlimited, default: 100)

**Example:**

```json
{
  "tool": "query_database",
  "arguments": {
    "query": "SELECT * FROM orders WHERE created_at > '2024-01-01' LIMIT 10",
    "timeout_seconds": 30,
    "max_rows": 100
  }
}
```

## Supported Databases

- PostgreSQL (recommended)
- MySQL
- SQLite
- Any SQLAlchemy-supported database

## Security Features

- **Read-only queries**: Only SELECT and WITH queries are allowed
- **Query timeout**: Configurable timeout to prevent long-running queries
- **Row limits**: Default limit of 100 rows per query (configurable)
- **Connection pooling**: Efficient connection management with pool recycling
- **URI sanitization**: Automatic conversion of legacy postgres:// to postgresql://

## Environment Variables

Required:

- `DATABASE_URL`: The database connection URL (e.g., `postgresql://user:pass@localhost:5432/mydb`)

Optional:

- `DATABASE_TOOLS_LOG_LEVEL`: Set logging level (default: INFO)
- `DATABASE_TOOLS_MAX_CONNECTIONS`: Maximum database connections per pool (default: 5)


## Error Handling

The server returns structured error responses:

```json
{
  "error": "Error message",
  "error_type": "ExceptionType",
  "recommendation": "Suggested action"
}
```

Common errors:

- Table/column not found: Check table names with `list_tables`
- Query timeout: Reduce query complexity or increase timeout
- Permission denied: Verify database credentials
