# Norma ORM

A modern Python ORM framework with dataclass support, providing type-safe database operations across PostgreSQL, SQLite, MongoDB, and Cassandra.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/Geoion/Norma.svg)](https://github.com/Geoion/Norma/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Geoion/Norma.svg)](https://github.com/Geoion/Norma/issues)

## 🚀 Features

- 🎯 **Type-Safe**: Built with modern Python type hints and full mypy support
- 🏗️ **Dataclass-Based**: Define models using Python dataclasses with automatic validation
- 🔄 **Multi-Database**: Unified interface for PostgreSQL, SQLite, MongoDB, and Cassandra
- 📊 **Schema Generation**: Automatic Pydantic schema generation for APIs
- ⚡ **Async/Sync**: Support for both asynchronous and synchronous operations
- 🛠️ **CLI Tools**: Powerful command-line interface for project initialization and code generation
- 🔍 **Query Builder**: Intuitive query syntax with support for complex filters
- 🔒 **Validation**: Built-in field validation with customizable constraints
- 📖 **Relationships**: Support for one-to-one, one-to-many, and many-to-many relationships
- 🎨 **Developer Experience**: Rich error messages and comprehensive debugging tools

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Models](#models)
- [Database Operations](#database-operations)
- [Schema Generation](#schema-generation)
- [CLI Tools](#cli-tools)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## 📦 Installation

### Basic Installation

```bash
pip install norma-orm
```

### Database-Specific Dependencies

```bash
# For PostgreSQL support
pip install norma-orm[postgres]

# For Cassandra support
pip install norma-orm[cassandra]

# For all development tools
pip install norma-orm[dev]

# For CLI tools with rich output
pip install norma-orm[cli]

# Install everything
pip install norma-orm[postgres,cassandra,dev,cli]
```

### From Source

```bash
git clone https://github.com/Geoion/Norma.git
cd Norma
pip install -e .
```

## ⚡ Quick Start

### 1. Define Your Models

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from norma import BaseModel, Field

@dataclass
class User(BaseModel):
    # Primary key with auto-generation
    id: str = Field(
        primary_key=True,
        default_factory=lambda: __import__('uuid').uuid4().hex,
        description="Unique user identifier"
    )
    
    # Required fields with validation
    name: str = Field(
        max_length=100,
        min_length=1,
        index=True,
        description="User's full name"
    )
    
    email: str = Field(
        unique=True,
        max_length=255,
        regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="User's email address"
    )
    
    # Optional fields with defaults
    age: int = Field(
        default=0,
        min_value=0,
        max_value=150,
        description="User's age in years"
    )
    
    is_active: bool = Field(
        default=True,
        index=True,
        description="Whether the user account is active"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Account creation timestamp"
    )
```

### 2. Initialize the Client

```python
from norma import NormaClient

# SQLite (for development)
client = NormaClient(
    adapter_type="sql",
    database_url="sqlite:///./app.db"
)

# PostgreSQL (for production)
client = NormaClient(
    adapter_type="sql",
    database_url="postgresql://user:password@localhost:5432/mydb"
)

# MongoDB
client = NormaClient(
    adapter_type="mongo",
    database_url="mongodb://localhost:27017",
    database_name="myapp"
)

# Cassandra
client = NormaClient(
    adapter_type="cassandra",
    database_url="127.0.0.1",
    keyspace="myapp_keyspace"
)
```

### 3. Basic CRUD Operations

```python
import asyncio

async def main():
    async with client:
        # Get model client
        user_client = client.get_model_client(User)
        
        # Create table/collection
        await user_client.create_table()
        
        # Create a user
        user = User(
            name="John Doe",
            email="john@example.com",
            age=30
        )
        created_user = await user_client.insert(user)
        print(f"Created: {created_user}")
        
        # Find by ID
        found_user = await user_client.find_by_id(created_user.id)
        print(f"Found: {found_user}")
        
        # Update user
        found_user.age = 31
        updated_user = await user_client.update(found_user)
        print(f"Updated: {updated_user}")
        
        # Query users
        adults = await user_client.find_many({"age": {"$gte": 18}})
        print(f"Adults: {len(adults)}")
        
        # Delete user
        deleted = await user_client.delete_by_id(created_user.id)
        print(f"Deleted: {deleted}")

# Run the example
asyncio.run(main())
```

## 🏗️ Models

### Defining Models

Models in Norma are Python dataclasses that inherit from `BaseModel`:

```python
from dataclasses import dataclass
from typing import Optional, List
from norma import BaseModel, Field, OneToMany, ManyToOne

@dataclass
class Author(BaseModel):
    id: str = Field(primary_key=True, default_factory=lambda: __import__('uuid').uuid4().hex)
    name: str = Field(max_length=100, index=True)
    email: str = Field(unique=True)
    bio: Optional[str] = Field(max_length=1000, default=None)

@dataclass
class Post(BaseModel):
    id: str = Field(primary_key=True, default_factory=lambda: __import__('uuid').uuid4().hex)
    title: str = Field(max_length=200, index=True)
    content: str = Field(min_length=1)
    published: bool = Field(default=False, index=True)
    
    # Foreign key relationship
    author_id: str = Field(
        relationship=ManyToOne("Author", foreign_key="id"),
        description="ID of the post author"
    )
    
    created_at: datetime = Field(default_factory=datetime.now, index=True)
```

### Field Configuration

The `Field()` function provides extensive configuration options:

```python
from norma import Field

# Basic field types
name: str = Field()  # Simple string field
age: int = Field(default=0)  # With default value
active: bool = Field(default=True)

# Validation constraints
email: str = Field(
    unique=True,                    # Unique constraint
    max_length=255,                 # Maximum string length
    min_length=5,                   # Minimum string length
    regex_pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"  # Regex validation
)

price: float = Field(
    min_value=0.0,                  # Minimum numeric value
    max_value=999999.99,            # Maximum numeric value
    default=0.0
)

# Database options
user_id: str = Field(
    primary_key=True,               # Primary key
    index=True,                     # Create database index
    nullable=False,                 # Not nullable
    db_column_name="user_uuid",     # Custom column name
    db_type="UUID"                  # Custom database type
)

# Documentation
description: str = Field(
    max_length=500,
    description="User-friendly field description"
)
```

### Relationships

Norma supports various relationship types:

```python
from norma import OneToOne, OneToMany, ManyToOne, ManyToMany

@dataclass
class User(BaseModel):
    id: str = Field(primary_key=True)
    name: str = Field()

@dataclass
class Profile(BaseModel):
    id: str = Field(primary_key=True)
    user_id: str = Field(relationship=OneToOne("User"))
    bio: str = Field()

@dataclass
class Post(BaseModel):
    id: str = Field(primary_key=True)
    author_id: str = Field(relationship=ManyToOne("User"))
    title: str = Field()

@dataclass
class Tag(BaseModel):
    id: str = Field(primary_key=True)
    name: str = Field()
    post_ids: List[str] = Field(relationship=ManyToMany("Post"))
```

## 💾 Database Operations

### Basic CRUD

```python
# Create
user = User(name="Alice", email="alice@example.com")
created_user = await user_client.insert(user)

# Read
user = await user_client.find_by_id("user_id")
users = await user_client.find_many()

# Update
user.age = 25
updated_user = await user_client.update(user)

# Delete
deleted = await user_client.delete_by_id("user_id")
```

### Advanced Queries

```python
# Filter by single field
active_users = await user_client.find_many({"is_active": True})

# Multiple filters
adult_active_users = await user_client.find_many({
    "age": {"$gte": 18},
    "is_active": True
})

# Comparison operators
users = await user_client.find_many({
    "age": {"$gte": 18, "$lte": 65},  # Between 18 and 65
    "name": {"$ne": "Admin"},         # Not equal to "Admin"
    "email": {"$in": ["user1@test.com", "user2@test.com"]}  # In list
})

# Pagination and sorting
users = await user_client.find_many(
    filters={"is_active": True},
    limit=10,
    offset=20,
    order_by=["-created_at", "name"]  # Desc by created_at, asc by name
)

# Count records
total_users = await user_client.count()
active_users_count = await user_client.count({"is_active": True})

# Check existence
user_exists = await user_client.exists({"email": "test@example.com"})
```

### Synchronous Operations

For scenarios where you need synchronous operations:

```python
# Synchronous client usage
with client:
    user_client = client.get_model_client(User)
    
    # Synchronous operations
    user = User(name="Sync User", email="sync@example.com")
    created_user = user_client.insert_sync(user)
    
    found_user = user_client.find_by_id_sync(created_user.id)
    
    users = user_client.find_many_sync({"is_active": True})
```

## 📊 Schema Generation

Norma automatically generates Pydantic schemas for API integration:

```python
from norma.schema import generate_schemas

# Generate all schemas
schemas = generate_schemas(User)

CreateUserSchema = schemas['create']  # For input validation
ReadUserSchema = schemas['read']      # For output serialization  
UpdateUserSchema = schemas['update']  # For partial updates

# Use with FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.post("/users/", response_model=ReadUserSchema)
async def create_user(user_data: CreateUserSchema):
    # Convert schema to model
    user = User.from_dict(user_data.model_dump())
    created_user = await user_client.insert(user)
    return created_user.to_dict()

@app.patch("/users/{user_id}", response_model=ReadUserSchema)
async def update_user(user_id: str, user_data: UpdateUserSchema):
    # Find existing user
    user = await user_client.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404)
    
    # Apply updates
    update_data = user_data.model_dump(exclude_none=True)
    user.update(**update_data)
    
    updated_user = await user_client.update(user)
    return updated_user.to_dict()
```

## 🛠️ CLI Tools

### Project Initialization

```bash
# Create a new project
norma init my-project

# With specific template and database
norma init my-project --template fastapi --database postgresql

# Available templates: basic, fastapi, django
# Available databases: sqlite, postgresql, mongodb, cassandra
```

This creates a complete project structure:

```
my-project/
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── post.py
├── schemas/
│   └── __init__.py
├── config/
│   ├── __init__.py
│   └── database.py
├── main.py
├── requirements.txt
└── README.md
```

### Schema Generation

```bash
# Generate Pydantic schemas from models
norma generate --models ./models --output ./schemas

# Watch for changes and auto-regenerate
norma generate --models ./models --output ./schemas --watch

# Different output formats
norma generate --models ./models --output ./schemas --format pydantic
```

### Version Information

```bash
norma version
```

## ⚙️ Configuration

### Database Configuration

```python
# config/database.py
import os

DATABASE_CONFIG = {
    "type": "postgresql",
    "url": os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db"),
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",
    "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
}

# For MongoDB
MONGODB_CONFIG = {
    "url": os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
    "database_name": os.getenv("MONGODB_DB", "myapp"),
    "server_selection_timeout": 5000,
    "max_pool_size": 100,
}
```

### Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# For MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=myapp

# For Cassandra
CASSANDRA_HOSTS=127.0.0.1,127.0.0.2,127.0.0.3
CASSANDRA_KEYSPACE=myapp_keyspace
CASSANDRA_PORT=9042
CASSANDRA_USERNAME=cassandra
CASSANDRA_PASSWORD=cassandra
```

### Client Configuration

```python
# Advanced client configuration
client = NormaClient(
    adapter_type="sql",
    database_url="postgresql://user:pass@localhost/db",
    echo=True,              # Log SQL queries
    pool_size=10,           # Connection pool size
    max_overflow=20,        # Max overflow connections
    pool_timeout=30,        # Pool timeout in seconds
    pool_recycle=3600,      # Recycle connections after 1 hour
)

# Cassandra client configuration
cassandra_client = NormaClient(
    adapter_type="cassandra",
    database_url="127.0.0.1,127.0.0.2,127.0.0.3",
    keyspace="myapp_keyspace",
    port=9042,
    username="cassandra",
    password="cassandra",
    protocol_version=4,
    connect_timeout=10,
    request_timeout=10,
)
```

## 🚀 Advanced Usage

### Custom Validation

```python
from norma.exceptions import ValidationError

@dataclass
class User(BaseModel):
    email: str = Field(unique=True)
    age: int = Field(min_value=0, max_value=150)
    
    def __post_init__(self):
        super().__post_init__()  # Call parent validation
        
        # Custom validation logic
        if self.age < 13 and "@" not in self.email:
            raise ValidationError("Users under 13 must have a valid email")
        
        # Domain-specific validation
        if self.email.endswith("@competitor.com"):
            raise ValidationError("Competitor emails not allowed")
```

### Error Handling

```python
from norma.exceptions import (
    NormaError, ValidationError, NotFoundError, 
    DuplicateError, ConnectionError
)

try:
    user = User(name="", email="invalid-email")  # Will raise ValidationError
    await user_client.insert(user)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Field: {e.field}, Value: {e.value}")

except DuplicateError as e:
    print(f"Duplicate entry: {e.message}")

except NotFoundError as e:
    print(f"Not found: {e.message}")

except ConnectionError as e:
    print(f"Database connection failed: {e.message}")

except NormaError as e:
    print(f"Norma error: {e.message}")
    print(f"Details: {e.details}")
```

## 📚 API Reference

### BaseModel

The base class for all Norma models.

```python
class BaseModel:
    def validate(self) -> None:
        """Validate the model according to field configurations."""
    
    def to_dict(self, exclude_none: bool = True, exclude_private: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary."""
    
    def update(self, **kwargs) -> None:
        """Update model fields with validation."""
    
    @classmethod
    def get_primary_key_field(cls) -> Optional[str]:
        """Get the primary key field name."""
    
    @classmethod
    def get_unique_fields(cls) -> List[str]:
        """Get all unique field names."""
    
    def is_persisted(self) -> bool:
        """Check if model has been saved to database."""
```

### NormaClient

Main client for database operations.

```python
class NormaClient:
    def __init__(self, adapter_type: str, database_url: str, **kwargs):
        """Initialize client with database configuration."""
    
    async def connect(self) -> None:
        """Connect to database."""
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
    
    def get_model_client(self, model_class: Type[BaseModel]) -> ModelClient:
        """Get client for specific model."""
    
    # Context manager support
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
```

### ModelClient

Client for operations on a specific model.

```python
class ModelClient:
    async def insert(self, model: BaseModel) -> BaseModel:
        """Insert new record."""
    
    async def update(self, model: BaseModel) -> BaseModel:
        """Update existing record."""
    
    async def find_by_id(self, id_value: Any) -> Optional[BaseModel]:
        """Find record by primary key."""
    
    async def find_many(self, filters: Dict = None, limit: int = None, 
                       offset: int = None, order_by: List[str] = None) -> List[BaseModel]:
        """Find multiple records."""
    
    async def delete_by_id(self, id_value: Any) -> bool:
        """Delete record by primary key."""
    
    async def count(self, filters: Dict = None) -> int:
        """Count matching records."""
    
    async def exists(self, filters: Dict) -> bool:
        """Check if records exist."""
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install norma-orm[dev]  # Make sure all dependencies are installed
   ```

2. **Database Connection Issues**
   ```python
   # Test your connection string
   client = NormaClient(adapter_type="sql", database_url="your_url_here")
   try:
       await client.connect()
       print("Connection successful!")
   except ConnectionError as e:
       print(f"Connection failed: {e}")
   ```

3. **Validation Errors**
   ```python
   # Enable detailed error reporting
   import logging
   logging.getLogger('norma').setLevel(logging.DEBUG)
   ```

4. **Performance Issues**
   ```python
   # Optimize queries with indexes
   name: str = Field(index=True)  # Add indexes to frequently queried fields
   
   # Use pagination for large datasets
   users = await user_client.find_many(limit=100, offset=0)
   ```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Geoion/Norma.git
cd Norma

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linting
black .
isort .
mypy norma/
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write** tests for your changes
4. **Ensure** tests pass and code is formatted
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Reporting Issues

When reporting issues, please include:

- Python version
- Norma version (`norma version`)
- Database type and version
- Minimal code example
- Full error traceback

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

