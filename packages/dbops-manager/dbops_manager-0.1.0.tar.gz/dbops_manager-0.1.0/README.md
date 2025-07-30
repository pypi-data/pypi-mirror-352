# dbops-manager

A flexible database operations manager supporting multiple databases with a focus on PostgreSQL.

## Features

- Modular database operations system
- PostgreSQL support with SQLAlchemy
- Flexible configuration through environment variables or programmatic setup
- Type-safe operations with proper error handling
- Singleton pattern for database connections
- Clean and extensible interface for database operations

## Installation

```bash
pip install dbops-manager
```

## Quick Start

1. Set up your database configuration either through environment variables or programmatically:

```python
from dbops_manager import settings

# Method 1: Using environment variables (.env file)
# DB_HOST=localhost
# DB_PORT=5432
# DB_USERNAME=postgres
# DB_PASSWORD=postgres
# DB_NAME=example

# Method 2: Configure programmatically
settings.configure(
    db_host='localhost',
    db_port=5432,
    db_username='postgres',
    db_password='postgres',
    db_name='example'
)
```

2. Define your model:

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

3. Use the database operations:

```python
from dbops_manager import PostgresOperations

# Initialize with your model
db = PostgresOperations(User)

# Create users
db.create_users([
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
])

# List all users
db.list_all_users()

# Update a user
db.update_user_info(1, {"name": "Alice Smith"})

# Delete a user
db.delete_user_by_id(2)
```

## Configuration

The package supports configuration through both environment variables and programmatic setup:

### Environment Variables

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_USERNAME`: Database username (default: postgres)
- `DB_PASSWORD`: Database password (default: postgres)
- `DB_NAME`: Database name (default: example)

### Programmatic Configuration

```python
from dbops_manager import settings

settings.configure(
    db_host='localhost',
    db_port=5432,
    db_username='user',
    db_password='pass',
    db_name='mydb'
)
```

## License

MIT License - see LICENSE file for details. 