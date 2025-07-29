"""
Norma Cassandra Adapter

Cassandra adapter using cassandra-driver for both sync and async operations.
Supports CQL queries and Cassandra-specific features.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar
from dataclasses import fields
from datetime import datetime
import uuid

try:
    from cassandra.cluster import Cluster, Session
    from cassandra.auth import PlainTextAuthProvider
    from cassandra.query import SimpleStatement, PreparedStatement
    from cassandra.policies import DCAwareRoundRobinPolicy
    from cassandra import InvalidRequest, AlreadyExists
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False
    Cluster = None
    Session = None
    PlainTextAuthProvider = None

from .base_adapter import BaseAdapter
from ..core.base_model import BaseModel
from ..core.field import FieldConfig
from ..exceptions import (
    ConnectionError, 
    NotFoundError, 
    DuplicateError, 
    QueryError,
    ValidationError,
    ConfigurationError
)


T = TypeVar('T', bound=BaseModel)


class CassandraAdapter(BaseAdapter):
    """
    Cassandra adapter using cassandra-driver.
    
    Provides CRUD operations for Apache Cassandra with CQL support.
    Handles keyspace management and table creation with appropriate data types.
    """
    
    def __init__(self, connection_string: str, keyspace: str, **kwargs):
        """
        Initialize Cassandra adapter.
        
        Args:
            connection_string: Cassandra contact points (comma-separated hosts)
            keyspace: Cassandra keyspace name
            **kwargs: Additional configuration options
        """
        if not CASSANDRA_AVAILABLE:
            raise ConfigurationError(
                "Cassandra driver not available. Install with: pip install cassandra-driver"
            )
        
        super().__init__(connection_string, **kwargs)
        
        self.keyspace = keyspace
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None
        
        # Parse connection configuration
        self.contact_points = [host.strip() for host in connection_string.split(',')]
        self.port = kwargs.get('port', 9042)
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.protocol_version = kwargs.get('protocol_version', 4)
        self.load_balancing_policy = kwargs.get('load_balancing_policy')
        
        # Connection options
        self.connect_timeout = kwargs.get('connect_timeout', 5)
        self.request_timeout = kwargs.get('request_timeout', 10)
        self.control_connection_timeout = kwargs.get('control_connection_timeout', 2)
        
        # Table tracking
        self.tables: Dict[str, str] = {}  # model_name -> table_name
        self.prepared_statements: Dict[str, PreparedStatement] = {}
    
    async def connect(self) -> None:
        """Establish connection to Cassandra cluster."""
        try:
            # Setup authentication if provided
            auth_provider = None
            if self.username and self.password:
                auth_provider = PlainTextAuthProvider(
                    username=self.username, 
                    password=self.password
                )
            
            # Setup load balancing policy
            load_balancing_policy = self.load_balancing_policy
            if not load_balancing_policy:
                load_balancing_policy = DCAwareRoundRobinPolicy()
            
            # Create cluster
            self.cluster = Cluster(
                contact_points=self.contact_points,
                port=self.port,
                auth_provider=auth_provider,
                protocol_version=self.protocol_version,
                load_balancing_policy=load_balancing_policy,
                connect_timeout=self.connect_timeout,
                control_connection_timeout=self.control_connection_timeout,
            )
            
            # Connect to cluster
            self.session = self.cluster.connect()
            self.session.default_timeout = self.request_timeout
            
            # Create keyspace if it doesn't exist
            await self._create_keyspace_if_not_exists()
            
            # Use the keyspace
            self.session.set_keyspace(self.keyspace)
            
            self._is_connected = True
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Cassandra: {str(e)}", self.connection_string)
    
    async def disconnect(self) -> None:
        """Close Cassandra connections."""
        try:
            if self.session:
                self.session.shutdown()
            if self.cluster:
                self.cluster.shutdown()
            self._is_connected = False
        except Exception:
            # Log error but don't raise - we're cleaning up
            pass
    
    async def _create_keyspace_if_not_exists(self) -> None:
        """Create keyspace if it doesn't exist."""
        create_keyspace_cql = f"""
        CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
        WITH REPLICATION = {{
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }}
        """
        
        try:
            self.session.execute(create_keyspace_cql)
        except Exception as e:
            raise QueryError(f"Failed to create keyspace {self.keyspace}: {str(e)}")
    
    async def create_table(self, model_class: Type[T]) -> None:
        """Create table for the given model."""
        table_name = self.get_table_name(model_class)
        
        if table_name in self.tables:
            return  # Table already defined
        
        # Build CREATE TABLE statement
        cql = self._build_create_table_cql(model_class, table_name)
        
        try:
            self.session.execute(cql)
            self.tables[table_name] = table_name
            
            # Create indexes
            await self._create_indexes(model_class, table_name)
            
        except AlreadyExists:
            # Table already exists, that's fine
            self.tables[table_name] = table_name
        except Exception as e:
            raise QueryError(f"Failed to create table {table_name}: {str(e)}")
    
    def _build_create_table_cql(self, model_class: Type[BaseModel], table_name: str) -> str:
        """Build CREATE TABLE CQL statement."""
        columns = []
        primary_key_fields = []
        
        for field_info in fields(model_class):
            field_name = field_info.name
            field_type = field_info.type
            config = field_info.metadata.get("norma_config")
            
            # Convert Python type to Cassandra type
            cql_type = self._python_type_to_cassandra(field_type, config)
            
            # Add column definition
            column_def = f"{field_name} {cql_type}"
            columns.append(column_def)
            
            # Track primary key fields
            if config and config.primary_key:
                primary_key_fields.append(field_name)
        
        # Ensure we have at least one primary key
        if not primary_key_fields:
            # If no explicit primary key, use 'id' field or create one
            id_field_exists = any(f.name == 'id' for f in fields(model_class))
            if id_field_exists:
                primary_key_fields = ['id']
            else:
                # Add a default primary key
                columns.append("id UUID")
                primary_key_fields = ['id']
        
        # Build primary key clause
        if len(primary_key_fields) == 1:
            primary_key_clause = f"PRIMARY KEY ({primary_key_fields[0]})"
        else:
            # For composite keys, first field is partition key, others are clustering keys
            partition_key = primary_key_fields[0]
            clustering_keys = ', '.join(primary_key_fields[1:])
            primary_key_clause = f"PRIMARY KEY ({partition_key}, {clustering_keys})"
        
        # Build complete CQL
        columns_clause = ',\n    '.join(columns)
        cql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_clause},
            {primary_key_clause}
        )
        """
        
        return cql
    
    def _python_type_to_cassandra(self, python_type: Type, config: Optional[FieldConfig] = None) -> str:
        """Convert Python type to Cassandra CQL type."""
        # Handle Optional types
        from typing import get_origin, get_args
        origin = get_origin(python_type)
        if origin is type(None) or (origin and type(None) in get_args(python_type)):
            # Extract the non-None type from Optional
            args = get_args(python_type)
            if args:
                python_type = next((arg for arg in args if arg is not type(None)), str)
        
        # Custom database type override
        if config and config.db_type:
            return config.db_type
        
        # Type mapping for Cassandra
        type_mapping = {
            str: "TEXT",
            int: "BIGINT",
            float: "DOUBLE", 
            bool: "BOOLEAN",
            datetime: "TIMESTAMP",
            bytes: "BLOB",
            uuid.UUID: "UUID",
        }
        
        # Handle string length constraints
        if python_type == str and config:
            if config.max_length and config.max_length <= 65535:
                return "VARCHAR"
            return "TEXT"
        
        return type_mapping.get(python_type, "TEXT")
    
    async def _create_indexes(self, model_class: Type[BaseModel], table_name: str) -> None:
        """Create secondary indexes for indexed fields."""
        for field_info in fields(model_class):
            config = field_info.metadata.get("norma_config")
            if not config:
                continue
            
            field_name = field_info.name
            
            # Create secondary indexes (not for primary key fields)
            if config.index and not config.primary_key:
                index_name = f"{table_name}_{field_name}_idx"
                create_index_cql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({field_name})"
                
                try:
                    self.session.execute(create_index_cql)
                except Exception as e:
                    # Index creation failures are usually not critical
                    pass
    
    async def drop_table(self, model_class: Type[T]) -> None:
        """Drop table for the given model."""
        table_name = self.get_table_name(model_class)
        
        try:
            drop_cql = f"DROP TABLE IF EXISTS {table_name}"
            self.session.execute(drop_cql)
            
            # Remove from our table registry
            if table_name in self.tables:
                del self.tables[table_name]
                
        except Exception as e:
            raise QueryError(f"Failed to drop table {table_name}: {str(e)}")
    
    async def insert(self, model: T) -> T:
        """Insert a new record."""
        self.validate_model(model)
        
        table_name = self.get_table_name(model.__class__)
        
        # Ensure table exists
        if table_name not in self.tables:
            await self.create_table(model.__class__)
        
        # Prepare data for insertion
        data = model.to_dict(exclude_none=False)
        
        # Generate primary key if needed
        pk_field = self.get_primary_key_field(model.__class__)
        if not data.get(pk_field):
            if pk_field == 'id':
                # Generate UUID for id field
                data[pk_field] = str(uuid.uuid4())
                setattr(model, pk_field, data[pk_field])
            else:
                data[pk_field] = model.generate_id()
                setattr(model, pk_field, data[pk_field])
        
        # Build INSERT statement
        fields_str = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.keys()])
        insert_cql = f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"
        
        try:
            self.session.execute(insert_cql, list(data.values()))
            return model
            
        except InvalidRequest as e:
            if "already exists" in str(e).lower():
                raise DuplicateError(f"Record with primary key already exists: {str(e)}")
            raise QueryError(f"Invalid request: {str(e)}")
        except Exception as e:
            raise QueryError(f"Failed to insert record: {str(e)}")
    
    async def update(self, model: T) -> T:
        """Update an existing record."""
        self.validate_model(model)
        
        table_name = self.get_table_name(model.__class__)
        
        if table_name not in self.tables:
            raise QueryError(f"Table {table_name} not found")
        
        pk_field = self.get_primary_key_field(model.__class__)
        pk_value = getattr(model, pk_field)
        
        if not pk_value:
            raise ValidationError(f"Primary key field '{pk_field}' is required for update")
        
        # Prepare data for update (exclude primary key)
        data = model.to_dict(exclude_none=False)
        update_data = {k: v for k, v in data.items() if k != pk_field}
        
        if not update_data:
            return model  # Nothing to update
        
        # Build UPDATE statement
        set_clause = ', '.join([f"{k} = ?" for k in update_data.keys()])
        update_cql = f"UPDATE {table_name} SET {set_clause} WHERE {pk_field} = ?"
        
        try:
            values = list(update_data.values()) + [pk_value]
            self.session.execute(update_cql, values)
            return model
            
        except Exception as e:
            raise QueryError(f"Failed to update record: {str(e)}")
    
    async def find_by_id(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Find a record by primary key."""
        table_name = self.get_table_name(model_class)
        
        if table_name not in self.tables:
            return None
        
        pk_field = self.get_primary_key_field(model_class)
        
        try:
            select_cql = f"SELECT * FROM {table_name} WHERE {pk_field} = ?"
            result = self.session.execute(select_cql, [id_value])
            row = result.one()
            
            if row:
                # Convert row to dictionary
                row_dict = dict(row._asdict())
                return model_class.from_dict(row_dict)
            
            return None
            
        except Exception as e:
            if "No rows" in str(e) or "not found" in str(e).lower():
                return None
            raise QueryError(f"Failed to find record: {str(e)}")
    
    async def find_many(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Find multiple records."""
        table_name = self.get_table_name(model_class)
        
        if table_name not in self.tables:
            return []
        
        # Build SELECT statement
        select_cql = f"SELECT * FROM {table_name}"
        values = []
        
        # Add WHERE clause
        if filters:
            where_conditions = []
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Handle operators - Cassandra has limited operator support
                    for op, op_value in value.items():
                        if op == "$eq" or op == "=":
                            where_conditions.append(f"{field} = ?")
                            values.append(op_value)
                        # Note: Cassandra doesn't support range queries without proper modeling
                        # This is a simplified implementation
                else:
                    where_conditions.append(f"{field} = ?")
                    values.append(value)
            
            if where_conditions:
                select_cql += " WHERE " + " AND ".join(where_conditions)
        
        # Add ordering (limited in Cassandra)
        if order_by:
            # Cassandra only allows ordering by clustering columns
            # This is a simplified implementation
            order_clause = []
            for field in order_by:
                if field.startswith('-'):
                    order_clause.append(f"{field[1:]} DESC")
                else:
                    order_clause.append(f"{field} ASC")
            if order_clause:
                select_cql += " ORDER BY " + ", ".join(order_clause)
        
        # Add limit
        if limit:
            select_cql += f" LIMIT {limit}"
        
        # Note: Cassandra doesn't support OFFSET, this is a limitation
        if offset:
            # In real implementation, you'd need to implement pagination differently
            pass
        
        try:
            result = self.session.execute(select_cql, values)
            
            models = []
            for row in result:
                row_dict = dict(row._asdict())
                models.append(model_class.from_dict(row_dict))
            
            return models
            
        except Exception as e:
            raise QueryError(f"Failed to find records: {str(e)}")
    
    async def delete_by_id(self, model_class: Type[T], id_value: Any) -> bool:
        """Delete a record by primary key."""
        table_name = self.get_table_name(model_class)
        
        if table_name not in self.tables:
            return False
        
        pk_field = self.get_primary_key_field(model_class)
        
        try:
            delete_cql = f"DELETE FROM {table_name} WHERE {pk_field} = ?"
            self.session.execute(delete_cql, [id_value])
            
            # Cassandra doesn't return affected row count, so we assume success
            return True
            
        except Exception as e:
            raise QueryError(f"Failed to delete record: {str(e)}")
    
    async def count(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records matching criteria."""
        table_name = self.get_table_name(model_class)
        
        if table_name not in self.tables:
            return 0
        
        # Build COUNT query
        count_cql = f"SELECT COUNT(*) FROM {table_name}"
        values = []
        
        # Add WHERE clause
        if filters:
            where_conditions = []
            for field, value in filters.items():
                where_conditions.append(f"{field} = ?")
                values.append(value)
            
            if where_conditions:
                count_cql += " WHERE " + " AND ".join(where_conditions)
        
        try:
            result = self.session.execute(count_cql, values)
            row = result.one()
            return row.count if row else 0
                    
        except Exception as e:
            raise QueryError(f"Failed to count records: {str(e)}")
    
    async def exists(
        self, 
        model_class: Type[T], 
        filters: Dict[str, Any]
    ) -> bool:
        """Check if records exist matching criteria."""
        count = await self.count(model_class, filters)
        return count > 0
    
    # Synchronous method implementations
    
    def connect_sync(self) -> None:
        """Synchronous version of connect."""
        # Run async connect in new event loop
        asyncio.run(self.connect())
    
    def insert_sync(self, model: T) -> T:
        """Synchronous version of insert."""
        return asyncio.run(self.insert(model))
    
    def update_sync(self, model: T) -> T:
        """Synchronous version of update."""
        return asyncio.run(self.update(model))
    
    def find_by_id_sync(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Synchronous version of find_by_id."""
        return asyncio.run(self.find_by_id(model_class, id_value))
    
    def find_many_sync(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Synchronous version of find_many."""
        return asyncio.run(self.find_many(model_class, filters, limit, offset, order_by))
    
    def delete_by_id_sync(self, model_class: Type[T], id_value: Any) -> bool:
        """Synchronous version of delete_by_id."""
        return asyncio.run(self.delete_by_id(model_class, id_value))
    
    def count_sync(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Synchronous version of count."""
        return asyncio.run(self.count(model_class, filters))
    
    def __enter__(self):
        """Sync context manager entry."""
        self.connect_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        asyncio.run(self.disconnect()) 