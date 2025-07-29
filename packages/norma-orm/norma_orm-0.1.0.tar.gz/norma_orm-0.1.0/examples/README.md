# Norma ORM Examples

This directory contains practical examples demonstrating various features of Norma ORM across different database systems.

## Examples Overview

### 🐘 [PostgreSQL Example](./postgres_example.py)
Demonstrates advanced PostgreSQL features including:
- **Complex Relationships**: OneToMany, ManyToOne relationships
- **Advanced Queries**: Filtering, sorting, pagination
- **PostgreSQL Features**: JSON fields, array operations
- **Schema Generation**: FastAPI integration with Pydantic

### 📄 [SQLite Example](./sqlite_example.py) 
Shows lightweight development workflows with:
- **Local Development**: File-based database setup
- **Quick Prototyping**: Rapid model iteration
- **Testing**: Perfect for unit tests
- **Embedded Applications**: Self-contained database

### 🍃 [MongoDB Example](./mongodb_example.py)
Explores NoSQL document modeling with:
- **Document Storage**: Flexible schema design
- **Embedded Documents**: Nested data structures
- **MongoDB Queries**: Document-based filtering
- **GridFS Support**: Large file storage

### ⚡ [Cassandra Example](./cassandra_example.py)
Demonstrates distributed database operations with:
- **Time-Series Data**: IoT sensor measurements
- **Partition Keys**: Efficient data distribution
- **Clustering Keys**: Time-based ordering
- **High Availability**: Distributed architecture
- **CQL Operations**: Cassandra Query Language

### 🚀 [FastAPI Integration](./fastapi_example.py)
Complete web API implementation featuring:
- **Automatic Schema Generation**: Pydantic models from Norma models
- **API Endpoints**: Full CRUD operations
- **Request Validation**: Type-safe input validation
- **Response Serialization**: Automatic JSON conversion
- **Database Integration**: Async database operations

### 🎯 [Advanced Features](./advanced_example.py)
Showcases enterprise-grade features:
- **Custom Validation**: Domain-specific rules
- **Error Handling**: Comprehensive exception management
- **Performance Optimization**: Connection pooling, indexing
- **Monitoring**: Query logging and metrics
- **Multi-Database**: Using multiple databases simultaneously

## Getting Started

### Prerequisites

```bash
# Install Norma with desired database support
pip install norma-orm[postgres,cassandra,dev]

# Or install specific database drivers
pip install norma-orm[postgres]  # PostgreSQL
pip install norma-orm[cassandra] # Cassandra
```

### Database Setup

#### PostgreSQL
```bash
# Using Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=norma_examples \
  -p 5432:5432 postgres:15

# Or install locally
brew install postgresql  # macOS
```

#### MongoDB
```bash
# Using Docker
docker run -d --name mongodb \
  -p 27017:27017 mongo:latest

# Or install locally
brew install mongodb/brew/mongodb-community  # macOS
```

#### Cassandra
```bash
# Using Docker
docker run -d --name cassandra \
  -p 9042:9042 cassandra:latest

# Wait for Cassandra to start (takes a few minutes)
docker logs cassandra

# Or install locally
brew install cassandra  # macOS
```

### Running Examples

1. **Choose your database example:**
   ```bash
   python postgres_example.py     # PostgreSQL
   python mongodb_example.py      # MongoDB  
   python cassandra_example.py    # Cassandra
   python sqlite_example.py       # SQLite (no setup needed)
   ```

2. **Try the FastAPI integration:**
   ```bash
   python fastapi_example.py
   # Then visit http://localhost:8000/docs
   ```

3. **Explore advanced features:**
   ```bash
   python advanced_example.py
   ```

## Example Patterns

### Basic CRUD Operations
All examples demonstrate the fundamental operations:
- **Create**: Insert new records
- **Read**: Query and retrieve data
- **Update**: Modify existing records  
- **Delete**: Remove records

### Database-Specific Features

#### SQL Databases (PostgreSQL, SQLite)
- Complex JOIN operations
- Advanced WHERE clauses
- Transaction management
- Index optimization

#### NoSQL Databases (MongoDB, Cassandra)
- Document/Column family modeling
- Denormalized data structures
- Distributed query patterns
- Eventual consistency handling

### Integration Patterns

#### Web Framework Integration
- FastAPI automatic schema generation
- Django model compatibility
- Flask-RESTful API patterns

#### Production Considerations
- Connection pooling
- Error handling strategies
- Monitoring and logging
- Performance optimization

## Contributing Examples

We welcome new examples! Please ensure your examples:

1. **Follow the pattern**: Use the existing example structure
2. **Include documentation**: Explain the concepts demonstrated
3. **Add error handling**: Show proper exception management
4. **Test thoroughly**: Verify examples work with latest Norma version

### Example Template

```python
"""
Your Example Title

Brief description of what this example demonstrates.
"""

import asyncio
from norma import BaseModel, Field, NormaClient
# ... other imports

# Define your models
@dataclass
class YourModel(BaseModel):
    # ... model definition

async def demonstrate_feature():
    """Demonstrate the specific feature."""
    # Implementation here
    pass

async def main():
    """Main example function."""
    print("🚀 Your Example Title")
    print("=" * 50)
    
    await demonstrate_feature()
    
    print("✅ Example completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database is running
   - Check connection string format
   - Ensure correct credentials

2. **Import Errors**
   - Install required dependencies
   - Check Python path configuration
   - Verify Norma installation

3. **Performance Issues**
   - Review query patterns
   - Check database indexes
   - Monitor connection pool usage

### Getting Help

- 📖 [Documentation](https://github.com/Geoion/Norma)
- 🐛 [Issues](https://github.com/Geoion/Norma/issues)
- 💬 [Discussions](https://github.com/Geoion/Norma/discussions)

---

**Happy coding with Norma ORM!** 🎉 