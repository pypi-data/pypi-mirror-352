"""
Norma Client

Main client class providing unified interface for database operations
across different adapters and models.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from dataclasses import is_dataclass

from .base_model import BaseModel
from ..adapters.base_adapter import BaseAdapter
from ..adapters.sql_adapter import SQLAdapter
from ..adapters.mongo_adapter import MongoAdapter
from ..adapters.cassandra_adapter import CassandraAdapter
from ..exceptions import ConfigurationError, NotFoundError


T = TypeVar('T', bound=BaseModel)


class ModelClient:
    """
    Client for a specific model providing CRUD operations.
    
    This class wraps the adapter operations and provides a clean interface
    for working with a specific model type.
    """
    
    def __init__(self, model_class: Type[T], adapter: BaseAdapter):
        """
        Initialize model client.
        
        Args:
            model_class: The model class this client operates on
            adapter: The database adapter to use
        """
        self.model_class = model_class
        self.adapter = adapter
        
        # Validate model class
        if not is_dataclass(model_class) or not issubclass(model_class, BaseModel):
            raise ConfigurationError(f"{model_class.__name__} must be a Norma BaseModel dataclass")
    
    async def insert(self, model: T) -> T:
        """Insert a new record."""
        return await self.adapter.insert(model)
    
    async def update(self, model: T) -> T:
        """Update an existing record."""
        return await self.adapter.update(model)
    
    async def find_by_id(self, id_value: Any) -> Optional[T]:
        """Find a record by its primary key."""
        return await self.adapter.find_by_id(self.model_class, id_value)
    
    async def find_many(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Find multiple records matching criteria."""
        return await self.adapter.find_many(
            self.model_class, filters, limit, offset, order_by
        )
    
    async def find_first(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None
    ) -> Optional[T]:
        """Find the first record matching criteria."""
        results = await self.find_many(filters, limit=1, order_by=order_by)
        return results[0] if results else None
    
    async def delete_by_id(self, id_value: Any) -> bool:
        """Delete a record by its primary key."""
        return await self.adapter.delete_by_id(self.model_class, id_value)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching criteria."""
        return await self.adapter.count(self.model_class, filters)
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if any records exist matching criteria."""
        return await self.adapter.exists(self.model_class, filters)
    
    async def create_table(self) -> None:
        """Create the table/collection for this model."""
        await self.adapter.create_table(self.model_class)
    
    async def drop_table(self) -> None:
        """Drop the table/collection for this model."""
        await self.adapter.drop_table(self.model_class)
    
    # Synchronous versions
    
    def insert_sync(self, model: T) -> T:
        """Synchronous version of insert."""
        return self.adapter.insert_sync(model)
    
    def update_sync(self, model: T) -> T:
        """Synchronous version of update."""
        return self.adapter.update_sync(model)
    
    def find_by_id_sync(self, id_value: Any) -> Optional[T]:
        """Synchronous version of find_by_id."""
        return self.adapter.find_by_id_sync(self.model_class, id_value)
    
    def find_many_sync(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Synchronous version of find_many."""
        return self.adapter.find_many_sync(
            self.model_class, filters, limit, offset, order_by
        )
    
    def find_first_sync(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None
    ) -> Optional[T]:
        """Synchronous version of find_first."""
        results = self.find_many_sync(filters, limit=1, order_by=order_by)
        return results[0] if results else None
    
    def delete_by_id_sync(self, id_value: Any) -> bool:
        """Synchronous version of delete_by_id."""
        return self.adapter.delete_by_id_sync(self.model_class, id_value)
    
    def count_sync(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Synchronous version of count."""
        return self.adapter.count_sync(self.model_class, filters)


class NormaClient:
    """
    Main Norma client providing unified database operations.
    
    This client manages the database adapter and provides model-specific
    clients for CRUD operations.
    """
    
    def __init__(
        self,
        adapter_type: str,
        database_url: str,
        database_name: Optional[str] = None,
        keyspace: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Norma client.
        
        Args:
            adapter_type: Type of adapter ('sql', 'mongo', or 'cassandra')
            database_url: Database connection URL
            database_name: Database name (required for MongoDB)
            keyspace: Keyspace name (required for Cassandra)
            **kwargs: Additional adapter configuration
        """
        self.adapter_type = adapter_type
        self.database_url = database_url
        self.database_name = database_name
        self.keyspace = keyspace
        self.config = kwargs
        
        # Initialize adapter
        self.adapter = self._create_adapter()
        
        # Model clients cache
        self._model_clients: Dict[Type[BaseModel], ModelClient] = {}
    
    def _create_adapter(self) -> BaseAdapter:
        """Create the appropriate adapter based on configuration."""
        if self.adapter_type == "sql":
            return SQLAdapter(self.database_url, **self.config)
        elif self.adapter_type == "mongo":
            if not self.database_name:
                raise ConfigurationError("database_name is required for MongoDB adapter")
            return MongoAdapter(self.database_url, self.database_name, **self.config)
        elif self.adapter_type == "cassandra":
            if not self.keyspace:
                raise ConfigurationError("keyspace is required for Cassandra adapter")
            return CassandraAdapter(self.database_url, self.keyspace, **self.config)
        else:
            raise ConfigurationError(f"Unsupported adapter type: {self.adapter_type}")
    
    async def connect(self) -> None:
        """Connect to the database."""
        await self.adapter.connect()
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        await self.adapter.disconnect()
    
    def get_model_client(self, model_class: Type[T]) -> ModelClient:
        """
        Get a model client for the specified model class.
        
        Args:
            model_class: The model class to get a client for
            
        Returns:
            ModelClient instance for the specified model
        """
        if model_class not in self._model_clients:
            self._model_clients[model_class] = ModelClient(model_class, self.adapter)
        return self._model_clients[model_class]
    
    def __getattr__(self, name: str) -> ModelClient:
        """
        Dynamic attribute access for model clients.
        
        Allows accessing model clients as client.user, client.post, etc.
        The model class is inferred from the attribute name.
        """
        # This is a simplified approach - in a real implementation,
        # you'd want to register model classes explicitly
        from ..core.base_model import BaseModel
        
        # Try to find a model class with this name
        # In a real implementation, you'd have a registry of models
        model_name = name.capitalize()
        
        # For now, raise an informative error
        raise AttributeError(
            f"Model client for '{name}' not found. "
            f"Use get_model_client(YourModelClass) to get a client for your model."
        )
    
    # Convenience methods for direct operations
    
    async def insert(self, model: T) -> T:
        """Insert a model instance."""
        client = self.get_model_client(model.__class__)
        return await client.insert(model)
    
    async def update(self, model: T) -> T:
        """Update a model instance."""
        client = self.get_model_client(model.__class__)
        return await client.update(model)
    
    async def find_by_id(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Find a record by ID."""
        client = self.get_model_client(model_class)
        return await client.find_by_id(id_value)
    
    async def find_many(
        self,
        model_class: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Find multiple records."""
        client = self.get_model_client(model_class)
        return await client.find_many(filters, limit, offset, order_by)
    
    async def delete_by_id(self, model_class: Type[T], id_value: Any) -> bool:
        """Delete a record by ID."""
        client = self.get_model_client(model_class)
        return await client.delete_by_id(id_value)
    
    async def count(self, model_class: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records."""
        client = self.get_model_client(model_class)
        return await client.count(filters)
    
    # Synchronous versions
    
    def connect_sync(self) -> None:
        """Synchronous version of connect."""
        if hasattr(self.adapter, 'connect_sync'):
            self.adapter.connect_sync()
        else:
            import asyncio
            asyncio.run(self.connect())
    
    def insert_sync(self, model: T) -> T:
        """Synchronous version of insert."""
        client = self.get_model_client(model.__class__)
        return client.insert_sync(model)
    
    def update_sync(self, model: T) -> T:
        """Synchronous version of update."""
        client = self.get_model_client(model.__class__)
        return client.update_sync(model)
    
    def find_by_id_sync(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Synchronous version of find_by_id."""
        client = self.get_model_client(model_class)
        return client.find_by_id_sync(id_value)
    
    def find_many_sync(
        self,
        model_class: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Synchronous version of find_many."""
        client = self.get_model_client(model_class)
        return client.find_many_sync(filters, limit, offset, order_by)
    
    def delete_by_id_sync(self, model_class: Type[T], id_value: Any) -> bool:
        """Synchronous version of delete_by_id."""
        client = self.get_model_client(model_class)
        return client.delete_by_id_sync(id_value)
    
    def count_sync(self, model_class: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Synchronous version of count."""
        client = self.get_model_client(model_class)
        return client.count_sync(filters)
    
    # Context manager support
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    def __enter__(self):
        """Sync context manager entry."""
        self.connect_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        import asyncio
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, create a task instead
            if loop.is_running():
                # For sync context manager in async context, we'll just disconnect the adapter directly
                if hasattr(self.adapter, 'disconnect_sync'):
                    self.adapter.disconnect_sync()
                else:
                    # Create a new event loop for disconnection
                    import threading
                    def disconnect_in_thread():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            new_loop.run_until_complete(self.disconnect())
                        finally:
                            new_loop.close()
                    
                    thread = threading.Thread(target=disconnect_in_thread)
                    thread.start()
                    thread.join()
            else:
                asyncio.run(self.disconnect())
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            asyncio.run(self.disconnect())
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected to database."""
        return self.adapter.is_connected 