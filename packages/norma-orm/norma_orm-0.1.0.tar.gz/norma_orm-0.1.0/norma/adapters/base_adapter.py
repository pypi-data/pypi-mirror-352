"""
Norma Base Adapter

Abstract base class defining the common interface for all database adapters.
Provides type-safe CRUD operations and connection management.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from dataclasses import fields

from ..core.base_model import BaseModel
from ..exceptions import NotFoundError, ConnectionError, QueryError


T = TypeVar('T', bound=BaseModel)


class BaseAdapter(ABC):
    """
    Abstract base class for all database adapters.
    
    Defines the standard interface that all adapters must implement
    to provide consistent CRUD operations across different databases.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize the adapter with connection parameters.
        
        Args:
            connection_string: Database connection string
            **kwargs: Additional adapter-specific configuration
        """
        self.connection_string = connection_string
        self.config = kwargs
        self._connection = None
        self._is_connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the database.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    async def create_table(self, model_class: Type[T]) -> None:
        """
        Create table/collection for the given model.
        
        Args:
            model_class: The model class to create table for
        """
        pass
    
    @abstractmethod
    async def drop_table(self, model_class: Type[T]) -> None:
        """
        Drop table/collection for the given model.
        
        Args:
            model_class: The model class to drop table for
        """
        pass
    
    @abstractmethod
    async def insert(self, model: T) -> T:
        """
        Insert a new record into the database.
        
        Args:
            model: The model instance to insert
            
        Returns:
            The inserted model with any auto-generated fields populated
            
        Raises:
            DuplicateError: If unique constraint is violated
            ValidationError: If model validation fails
        """
        pass
    
    @abstractmethod
    async def update(self, model: T) -> T:
        """
        Update an existing record in the database.
        
        Args:
            model: The model instance to update
            
        Returns:
            The updated model
            
        Raises:
            NotFoundError: If record doesn't exist
            ValidationError: If model validation fails
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """
        Find a record by its primary key.
        
        Args:
            model_class: The model class to search for
            id_value: The primary key value
            
        Returns:
            The found model or None if not found
        """
        pass
    
    @abstractmethod
    async def find_many(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """
        Find multiple records matching the given criteria.
        
        Args:
            model_class: The model class to search for
            filters: Dictionary of field filters
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: List of fields to order by
            
        Returns:
            List of matching models
        """
        pass
    
    @abstractmethod
    async def delete_by_id(self, model_class: Type[T], id_value: Any) -> bool:
        """
        Delete a record by its primary key.
        
        Args:
            model_class: The model class
            id_value: The primary key value
            
        Returns:
            True if record was deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def count(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records matching the given criteria.
        
        Args:
            model_class: The model class to count
            filters: Dictionary of field filters
            
        Returns:
            Number of matching records
        """
        pass
    
    @abstractmethod
    async def exists(
        self, 
        model_class: Type[T], 
        filters: Dict[str, Any]
    ) -> bool:
        """
        Check if any records exist matching the given criteria.
        
        Args:
            model_class: The model class to check
            filters: Dictionary of field filters
            
        Returns:
            True if any records exist, False otherwise
        """
        pass
    
    # Synchronous versions of methods for backward compatibility
    
    def insert_sync(self, model: T) -> T:
        """Synchronous version of insert."""
        raise NotImplementedError("Synchronous operations not supported by this adapter")
    
    def update_sync(self, model: T) -> T:
        """Synchronous version of update."""
        raise NotImplementedError("Synchronous operations not supported by this adapter")
    
    def find_by_id_sync(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Synchronous version of find_by_id."""
        raise NotImplementedError("Synchronous operations not supported by this adapter")
    
    def find_many_sync(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Synchronous version of find_many."""
        raise NotImplementedError("Synchronous operations not supported by this adapter")
    
    def delete_by_id_sync(self, model_class: Type[T], id_value: Any) -> bool:
        """Synchronous version of delete_by_id."""
        raise NotImplementedError("Synchronous operations not supported by this adapter")
    
    def count_sync(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Synchronous version of count."""
        raise NotImplementedError("Synchronous operations not supported by this adapter")
    
    # Utility methods
    
    def get_table_name(self, model_class: Type[BaseModel]) -> str:
        """
        Get the table/collection name for a model class.
        
        Default implementation uses the lowercase class name.
        Can be overridden in subclasses for custom naming conventions.
        """
        return model_class.__name__.lower()
    
    def get_primary_key_field(self, model_class: Type[BaseModel]) -> str:
        """Get the primary key field name for a model class."""
        pk_field = model_class.get_primary_key_field()
        if not pk_field:
            raise ValueError(f"Model {model_class.__name__} has no primary key field")
        return pk_field
    
    def validate_model(self, model: BaseModel) -> None:
        """Validate a model instance."""
        try:
            model.validate()
        except Exception as e:
            raise QueryError(f"Model validation failed: {str(e)}")
    
    def _get_field_names(self, model_class: Type[BaseModel]) -> List[str]:
        """Get all field names for a model class."""
        return [field.name for field in fields(model_class)]
    
    def _filter_model_data(self, data: Dict[str, Any], model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Filter dictionary to only include fields that exist in the model."""
        valid_fields = set(self._get_field_names(model_class))
        return {k: v for k, v in data.items() if k in valid_fields}
    
    @property
    def is_connected(self) -> bool:
        """Check if adapter is connected to the database."""
        return self._is_connected
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    def __enter__(self):
        """Sync context manager entry (for sync adapters)."""
        # This should be overridden in sync adapters
        raise NotImplementedError("Synchronous context manager not supported by this adapter")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit (for sync adapters)."""
        # This should be overridden in sync adapters
        pass 