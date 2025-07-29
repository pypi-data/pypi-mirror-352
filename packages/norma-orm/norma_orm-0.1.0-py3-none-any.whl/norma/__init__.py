"""
Norma ORM - A modern Python ORM framework

A type-safe, dataclass-based ORM that supports PostgreSQL, SQLite, MongoDB, and Cassandra
with automatic Pydantic schema generation.
"""

from .core.base_model import BaseModel
from .core.field import Field, OneToOne, OneToMany, ManyToOne, ManyToMany
from .core.client import NormaClient
from .adapters.base_adapter import BaseAdapter
from .adapters.sql_adapter import SQLAdapter
from .adapters.mongo_adapter import MongoAdapter
from .adapters.cassandra_adapter import CassandraAdapter
from .schema.generator import SchemaGenerator
from .exceptions import (
    NormaError,
    ValidationError,
    NotFoundError,
    ConnectionError,
    DuplicateError,
)

__version__ = "0.1.0"
__author__ = "Geoion"
__email__ = "eski.yin@gmail.com"

__all__ = [
    # Core components
    "BaseModel",
    "Field", 
    "NormaClient",
    
    # Relationships
    "OneToOne",
    "OneToMany", 
    "ManyToOne",
    "ManyToMany",
    
    # Adapters
    "BaseAdapter",
    "SQLAdapter",
    "MongoAdapter",
    "CassandraAdapter",
    
    # Schema generation
    "SchemaGenerator",
    
    # Exceptions
    "NormaError",
    "ValidationError", 
    "NotFoundError",
    "ConnectionError",
    "DuplicateError",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
] 