"""
Norma Database Adapters

This package contains database adapters for different database systems.
"""

from .base_adapter import BaseAdapter
from .sql_adapter import SQLAdapter
from .mongo_adapter import MongoAdapter
from .cassandra_adapter import CassandraAdapter

__all__ = [
    "BaseAdapter",
    "SQLAdapter", 
    "MongoAdapter",
    "CassandraAdapter",
] 