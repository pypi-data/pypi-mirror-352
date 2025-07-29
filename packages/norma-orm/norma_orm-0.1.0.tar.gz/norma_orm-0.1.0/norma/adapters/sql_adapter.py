"""
Norma SQL Adapter

SQLAlchemy-based adapter for SQL databases (PostgreSQL, SQLite, MySQL).
Supports both synchronous and asynchronous operations.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, get_origin, get_args
from dataclasses import fields
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Index
from sqlalchemy.sql import select, insert, update, delete
from sqlalchemy.exc import IntegrityError, NoResultFound

from .base_adapter import BaseAdapter
from ..core.base_model import BaseModel
from ..core.field import FieldConfig
from ..exceptions import (
    ConnectionError, 
    NotFoundError, 
    DuplicateError, 
    QueryError,
    ValidationError
)


T = TypeVar('T', bound=BaseModel)


class SQLAdapter(BaseAdapter):
    """
    SQL database adapter using SQLAlchemy Core.
    
    Supports PostgreSQL, SQLite, and MySQL with both sync and async operations.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize SQL adapter.
        
        Args:
            connection_string: SQLAlchemy connection string
            **kwargs: Additional configuration options
        """
        super().__init__(connection_string, **kwargs)
        
        self.metadata = MetaData()
        self.tables: Dict[str, Table] = {}
        
        # Configuration
        self.echo = kwargs.get('echo', False)
        self.pool_size = kwargs.get('pool_size', 5)
        self.max_overflow = kwargs.get('max_overflow', 10)
        
        # Engines and sessions
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
    
    async def connect(self) -> None:
        """Establish connection to the database."""
        try:
            # Create async engine
            if self.connection_string.startswith(('postgresql+asyncpg', 'sqlite+aiosqlite')):
                self._async_engine = create_async_engine(
                    self.connection_string,
                    echo=self.echo,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                )
                self._async_session_factory = sessionmaker(
                    self._async_engine, 
                    class_=AsyncSession, 
                    expire_on_commit=False
                )
            
            # Create sync engine (convert async URL to sync if needed)
            sync_url = self.connection_string
            if sync_url.startswith('postgresql+asyncpg'):
                sync_url = sync_url.replace('postgresql+asyncpg', 'postgresql+psycopg2')
            elif sync_url.startswith('sqlite+aiosqlite'):
                sync_url = sync_url.replace('sqlite+aiosqlite', 'sqlite')
            
            self._engine = create_engine(
                sync_url,
                echo=self.echo,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
            )
            self._session_factory = sessionmaker(self._engine)
            
            # Test connection
            if self._async_engine:
                async with self._async_engine.begin() as conn:
                    await conn.execute(sa.text("SELECT 1"))
            else:
                with self._engine.begin() as conn:
                    conn.execute(sa.text("SELECT 1"))
            
            self._is_connected = True
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}", self.connection_string)
    
    async def disconnect(self) -> None:
        """Close database connections."""
        try:
            if self._async_engine:
                await self._async_engine.dispose()
            if self._engine:
                self._engine.dispose()
            self._is_connected = False
        except Exception as e:
            # Log error but don't raise - we're cleaning up
            pass
    
    async def create_table(self, model_class: Type[T]) -> None:
        """Create table for the given model."""
        table_name = self.get_table_name(model_class)
        
        if table_name in self.tables:
            return  # Table already defined
        
        # Create SQLAlchemy table from model
        table = self._create_table_from_model(model_class, table_name)
        self.tables[table_name] = table
        
        # Create table in database
        try:
            if self._async_engine:
                async with self._async_engine.begin() as conn:
                    await conn.run_sync(self.metadata.create_all)
            else:
                self.metadata.create_all(self._engine)
        except Exception as e:
            raise QueryError(f"Failed to create table {table_name}: {str(e)}")
    
    async def drop_table(self, model_class: Type[T]) -> None:
        """Drop table for the given model."""
        table_name = self.get_table_name(model_class)
        
        # Create table object if not in registry (for existing tables)
        if table_name not in self.tables:
            self.tables[table_name] = self._create_table_from_model(model_class, table_name)
        
        table = self.tables[table_name]
        
        try:
            if self._async_engine:
                async with self._async_engine.begin() as conn:
                    await conn.run_sync(table.drop, checkfirst=True)
            else:
                table.drop(self._engine, checkfirst=True)
            
            # Remove from our table registry and metadata
            del self.tables[table_name]
            if table_name in self.metadata.tables:
                self.metadata.remove(table)
            
        except Exception as e:
            raise QueryError(f"Failed to drop table {table_name}: {str(e)}")
    
    def _create_table_from_model(self, model_class: Type[BaseModel], table_name: str) -> Table:
        """Create SQLAlchemy Table from Norma model."""
        columns = []
        indexes = []
        
        for field_info in fields(model_class):
            field_name = field_info.name
            field_type = field_info.type
            config = field_info.metadata.get("norma_config")
            
            # Convert Python type to SQLAlchemy type
            sa_type = self._python_type_to_sqlalchemy(field_type, config)
            
            # Create column
            column = Column(
                config.db_column_name or field_name,
                sa_type,
                primary_key=config.primary_key if config else False,
                unique=config.unique if config else False,
                nullable=config.nullable if config else True,
                default=config.default if config and config.default is not None else None,
            )
            columns.append(column)
            
            # Create indexes
            if config and config.index and not config.primary_key and not config.unique:
                index = Index(f"idx_{table_name}_{field_name}", column)
                indexes.append(index)
        
        # Create table
        table = Table(table_name, self.metadata, *columns, *indexes)
        return table
    
    def _python_type_to_sqlalchemy(self, python_type: Type, config: Optional[FieldConfig] = None) -> sa.types.TypeEngine:
        """Convert Python type to SQLAlchemy type."""
        # Handle Optional types
        origin = get_origin(python_type)
        if origin is type(None) or (origin and type(None) in get_args(python_type)):
            # Extract the non-None type from Optional
            args = get_args(python_type)
            if args:
                python_type = next((arg for arg in args if arg is not type(None)), str)
        
        # Custom database type override
        if config and config.db_type:
            return sa.text(config.db_type)
        
        # Type mapping
        type_mapping = {
            str: sa.String(config.max_length if config and config.max_length else 255),
            int: sa.Integer,
            float: sa.Float,
            bool: sa.Boolean,
            datetime: sa.DateTime,
            bytes: sa.LargeBinary,
        }
        
        return type_mapping.get(python_type, sa.String(255))
    
    async def insert(self, model: T) -> T:
        """Insert a new record."""
        self.validate_model(model)
        
        table_name = self.get_table_name(model.__class__)
        table = self.tables.get(table_name)
        
        if table is None:
            await self.create_table(model.__class__)
            table = self.tables[table_name]
        
        # Prepare data for insertion
        data = model.to_dict(exclude_none=False)
        
        # Generate primary key if needed
        pk_field = self.get_primary_key_field(model.__class__)
        if not data.get(pk_field):
            data[pk_field] = model.generate_id()
            setattr(model, pk_field, data[pk_field])
        
        try:
            if self._async_engine:
                async with self._async_session_factory() as session:
                    result = await session.execute(insert(table).values(**data))
                    await session.commit()
            else:
                with self._session_factory() as session:
                    result = session.execute(insert(table).values(**data))
                    session.commit()
            
            return model
            
        except IntegrityError as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise DuplicateError(f"Duplicate value for unique field: {str(e)}")
            raise QueryError(f"Database integrity error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Failed to insert record: {str(e)}")
    
    async def update(self, model: T) -> T:
        """Update an existing record."""
        self.validate_model(model)
        
        table_name = self.get_table_name(model.__class__)
        table = self.tables.get(table_name)
        
        if table is None:
            raise QueryError(f"Table {table_name} not found")
        
        pk_field = self.get_primary_key_field(model.__class__)
        pk_value = getattr(model, pk_field)
        
        if not pk_value:
            raise ValidationError(f"Primary key field '{pk_field}' is required for update")
        
        # Prepare data for update (exclude primary key)
        data = {k: v for k, v in model.to_dict(exclude_none=False).items() if k != pk_field}
        
        try:
            if self._async_engine:
                async with self._async_session_factory() as session:
                    result = await session.execute(
                        update(table).where(table.c[pk_field] == pk_value).values(**data)
                    )
                    await session.commit()
                    
                    if result.rowcount == 0:
                        raise NotFoundError(f"Record with {pk_field}={pk_value} not found")
            else:
                with self._session_factory() as session:
                    result = session.execute(
                        update(table).where(table.c[pk_field] == pk_value).values(**data)
                    )
                    session.commit()
                    
                    if result.rowcount == 0:
                        raise NotFoundError(f"Record with {pk_field}={pk_value} not found")
            
            return model
            
        except NotFoundError:
            raise
        except Exception as e:
            raise QueryError(f"Failed to update record: {str(e)}")
    
    async def find_by_id(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Find a record by primary key."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return None
        
        pk_field = self.get_primary_key_field(model_class)
        
        try:
            if self._async_engine:
                async with self._async_session_factory() as session:
                    result = await session.execute(
                        select(table).where(table.c[pk_field] == id_value)
                    )
                    row = result.fetchone()
            else:
                with self._session_factory() as session:
                    result = session.execute(
                        select(table).where(table.c[pk_field] == id_value)
                    )
                    row = result.fetchone()
            
            if row:
                return model_class.from_dict(dict(row._mapping))
            return None
            
        except Exception as e:
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
        table = self.tables.get(table_name)
        
        if table is None:
            return []
        
        # Build query
        query = select(table)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(table.c, field):
                    if isinstance(value, dict):
                        # Handle operators like {"$gte": 18}
                        for op, op_value in value.items():
                            if op == "$gte":
                                query = query.where(table.c[field] >= op_value)
                            elif op == "$lte":
                                query = query.where(table.c[field] <= op_value)
                            elif op == "$gt":
                                query = query.where(table.c[field] > op_value)
                            elif op == "$lt":
                                query = query.where(table.c[field] < op_value)
                            elif op == "$ne":
                                query = query.where(table.c[field] != op_value)
                            elif op == "$in":
                                query = query.where(table.c[field].in_(op_value))
                    else:
                        query = query.where(table.c[field] == value)
        
        # Apply ordering
        if order_by:
            for field in order_by:
                if field.startswith('-'):
                    field = field[1:]
                    if hasattr(table.c, field):
                        query = query.order_by(table.c[field].desc())
                else:
                    if hasattr(table.c, field):
                        query = query.order_by(table.c[field])
        
        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        try:
            if self._async_engine:
                async with self._async_session_factory() as session:
                    result = await session.execute(query)
                    rows = result.fetchall()
            else:
                with self._session_factory() as session:
                    result = session.execute(query)
                    rows = result.fetchall()
            
            return [model_class.from_dict(dict(row._mapping)) for row in rows]
            
        except Exception as e:
            raise QueryError(f"Failed to find records: {str(e)}")
    
    async def delete_by_id(self, model_class: Type[T], id_value: Any) -> bool:
        """Delete a record by primary key."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return False
        
        pk_field = self.get_primary_key_field(model_class)
        
        try:
            if self._async_engine:
                async with self._async_session_factory() as session:
                    result = await session.execute(
                        delete(table).where(table.c[pk_field] == id_value)
                    )
                    await session.commit()
            else:
                with self._session_factory() as session:
                    result = session.execute(
                        delete(table).where(table.c[pk_field] == id_value)
                    )
                    session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            raise QueryError(f"Failed to delete record: {str(e)}")
    
    async def count(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records matching criteria."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return 0
        
        query = select(sa.func.count()).select_from(table)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(table.c, field):
                    query = query.where(table.c[field] == value)
        
        try:
            if self._async_engine:
                async with self._async_session_factory() as session:
                    result = await session.execute(query)
                    return result.scalar()
            else:
                with self._session_factory() as session:
                    result = session.execute(query)
                    return result.scalar()
                    
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
        if self._is_connected:
            return
            
        # Create synchronous engine and session factory
        engine_kwargs = {
            'echo': self.echo,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
        }
        self._sync_engine = sa.create_engine(self.connection_string, **engine_kwargs)
        self._session_factory = sessionmaker(bind=self._sync_engine)
        self._is_connected = True
    
    def insert_sync(self, model: T) -> T:
        """Synchronous version of insert."""
        self.validate_model(model)
        
        table_name = self.get_table_name(model.__class__)
        table = self.tables.get(table_name)
        
        if table is None:
            # Create table if it doesn't exist
            table = self._create_table_from_model(model.__class__, table_name)
            table.create(self._sync_engine, checkfirst=True)
            self.tables[table_name] = table
        
        # Prepare data for insertion
        data = model.to_dict(exclude_none=False)
        
        # Generate primary key if needed
        pk_field = self.get_primary_key_field(model.__class__)
        if not data.get(pk_field):
            data[pk_field] = model.generate_id()
            setattr(model, pk_field, data[pk_field])
        
        try:
            with self._session_factory() as session:
                result = session.execute(insert(table).values(**data))
                session.commit()
            return model
            
        except sa.exc.IntegrityError as e:
            raise DuplicateError(f"Duplicate value for unique field: {str(e)}")
        except Exception as e:
            raise QueryError(f"Failed to insert record: {str(e)}")
    
    def update_sync(self, model: T) -> T:
        """Synchronous version of update."""
        self.validate_model(model)
        
        table_name = self.get_table_name(model.__class__)
        table = self.tables.get(table_name)
        
        if table is None:
            raise QueryError(f"Table {table_name} not found")
        
        pk_field = self.get_primary_key_field(model.__class__)
        pk_value = getattr(model, pk_field)
        
        if not pk_value:
            raise ValidationError(f"Primary key field '{pk_field}' is required for update")
        
        data = {k: v for k, v in model.to_dict(exclude_none=False).items() if k != pk_field}
        
        try:
            with self._session_factory() as session:
                result = session.execute(
                    update(table).where(table.c[pk_field] == pk_value).values(**data)
                )
                session.commit()
                
                if result.rowcount == 0:
                    raise NotFoundError(f"Record with {pk_field}={pk_value} not found")
            
            return model
            
        except NotFoundError:
            raise
        except Exception as e:
            raise QueryError(f"Failed to update record: {str(e)}")
    
    def find_by_id_sync(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Synchronous version of find_by_id."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return None
        
        pk_field = self.get_primary_key_field(model_class)
        
        try:
            with self._session_factory() as session:
                result = session.execute(
                    select(table).where(table.c[pk_field] == id_value)
                )
                row = result.fetchone()
            
            if row:
                return model_class.from_dict(dict(row._mapping))
            return None
            
        except Exception as e:
            raise QueryError(f"Failed to find record: {str(e)}")
    
    def find_many_sync(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Synchronous version of find_many."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return []
        
        query = select(table)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(table.c, field):
                    if isinstance(value, dict):
                        for op, op_value in value.items():
                            if op == "$gte":
                                query = query.where(table.c[field] >= op_value)
                            elif op == "$lte":
                                query = query.where(table.c[field] <= op_value)
                            elif op == "$gt":
                                query = query.where(table.c[field] > op_value)
                            elif op == "$lt":
                                query = query.where(table.c[field] < op_value)
                            elif op == "$ne":
                                query = query.where(table.c[field] != op_value)
                            elif op == "$in":
                                query = query.where(table.c[field].in_(op_value))
                    else:
                        query = query.where(table.c[field] == value)
        
        # Apply ordering
        if order_by:
            for field in order_by:
                if field.startswith('-'):
                    field = field[1:]
                    if hasattr(table.c, field):
                        query = query.order_by(table.c[field].desc())
                else:
                    if hasattr(table.c, field):
                        query = query.order_by(table.c[field])
        
        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        try:
            with self._session_factory() as session:
                result = session.execute(query)
                rows = result.fetchall()
            
            return [model_class.from_dict(dict(row._mapping)) for row in rows]
            
        except Exception as e:
            raise QueryError(f"Failed to find records: {str(e)}")
    
    def delete_by_id_sync(self, model_class: Type[T], id_value: Any) -> bool:
        """Synchronous version of delete_by_id."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return False
        
        pk_field = self.get_primary_key_field(model_class)
        
        try:
            with self._session_factory() as session:
                result = session.execute(
                    delete(table).where(table.c[pk_field] == id_value)
                )
                session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            raise QueryError(f"Failed to delete record: {str(e)}")
    
    def count_sync(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Synchronous version of count."""
        table_name = self.get_table_name(model_class)
        table = self.tables.get(table_name)
        
        if table is None:
            return 0
        
        query = select(sa.func.count()).select_from(table)
        
        if filters:
            for field, value in filters.items():
                if hasattr(table.c, field):
                    query = query.where(table.c[field] == value)
        
        try:
            with self._session_factory() as session:
                result = session.execute(query)
                return result.scalar()
                    
        except Exception as e:
            raise QueryError(f"Failed to count records: {str(e)}")
    
    def disconnect_sync(self) -> None:
        """Synchronous version of disconnect."""
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
        self._session_factory = None
        self._is_connected = False
    
    def __enter__(self):
        """Sync context manager entry."""
        self.connect_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        self.disconnect_sync() 