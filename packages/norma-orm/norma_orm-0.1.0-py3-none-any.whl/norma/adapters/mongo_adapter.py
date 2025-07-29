"""
Norma MongoDB Adapter

Motor-based adapter for MongoDB with async operations.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar
from dataclasses import fields
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure

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


class MongoAdapter(BaseAdapter):
    """
    MongoDB adapter using Motor for async operations.
    
    Provides full CRUD operations with MongoDB-specific query syntax.
    """
    
    def __init__(self, connection_string: str, database_name: str, **kwargs):
        """
        Initialize MongoDB adapter.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to use
            **kwargs: Additional configuration options
        """
        super().__init__(connection_string, **kwargs)
        
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.sync_client: Optional[MongoClient] = None
        self.sync_database = None
        
        # Configuration
        self.server_selection_timeout = kwargs.get('server_selection_timeout', 5000)
        self.max_pool_size = kwargs.get('max_pool_size', 100)
        
        # Collection tracking
        self.collections: Dict[str, AsyncIOMotorCollection] = {}
        self.sync_collections: Dict[str, Any] = {}
    
    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            # Create async client
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=self.server_selection_timeout,
                maxPoolSize=self.max_pool_size
            )
            self.database = self.client[self.database_name]
            
            # Create sync client for synchronous operations
            self.sync_client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=self.server_selection_timeout,
                maxPoolSize=self.max_pool_size
            )
            self.sync_database = self.sync_client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            self._is_connected = True
            
        except ConnectionFailure as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}", self.connection_string)
        except Exception as e:
            raise ConnectionError(f"Unexpected error connecting to MongoDB: {str(e)}", self.connection_string)
    
    async def disconnect(self) -> None:
        """Close MongoDB connections."""
        try:
            if self.client:
                self.client.close()
            if self.sync_client:
                self.sync_client.close()
            self._is_connected = False
        except Exception:
            # Log error but don't raise - we're cleaning up
            pass
    
    async def create_table(self, model_class: Type[T]) -> None:
        """Create collection and indexes for the given model."""
        collection_name = self.get_table_name(model_class)
        
        if collection_name in self.collections:
            return  # Collection already set up
        
        # Get collection
        collection = self.database[collection_name]
        sync_collection = self.sync_database[collection_name]
        
        self.collections[collection_name] = collection
        self.sync_collections[collection_name] = sync_collection
        
        # Create indexes based on model fields
        await self._create_indexes(model_class, collection)
    
    async def _create_indexes(self, model_class: Type[BaseModel], collection: AsyncIOMotorCollection) -> None:
        """Create indexes for the model fields."""
        indexes = []
        
        for field_info in fields(model_class):
            config = field_info.metadata.get("norma_config")
            if not config:
                continue
            
            field_name = field_info.name
            
            # Primary key index (unique)
            if config.primary_key:
                indexes.append(IndexModel([(field_name, ASCENDING)], unique=True, name=f"pk_{field_name}"))
            
            # Unique indexes
            elif config.unique:
                indexes.append(IndexModel([(field_name, ASCENDING)], unique=True, name=f"unique_{field_name}"))
            
            # Regular indexes
            elif config.index:
                indexes.append(IndexModel([(field_name, ASCENDING)], name=f"idx_{field_name}"))
        
        # Create indexes if any
        if indexes:
            try:
                await collection.create_indexes(indexes)
            except Exception as e:
                # Log warning but don't fail - indexes might already exist
                pass
    
    async def drop_table(self, model_class: Type[T]) -> None:
        """Drop collection for the given model."""
        collection_name = self.get_table_name(model_class)
        
        if collection_name not in self.collections:
            return  # Collection doesn't exist
        
        try:
            # Drop the collection
            await self.database.drop_collection(collection_name)
            
            # Remove from our collection registry
            del self.collections[collection_name]
            if collection_name in self.sync_collections:
                del self.sync_collections[collection_name]
                
        except Exception as e:
            raise QueryError(f"Failed to drop collection {collection_name}: {str(e)}")
    
    def get_collection_name(self, model_class: Type[BaseModel]) -> str:
        """Get collection name for a model (alias for get_table_name)."""
        return self.get_table_name(model_class)
    
    async def insert(self, model: T) -> T:
        """Insert a new document."""
        self.validate_model(model)
        
        collection_name = self.get_collection_name(model.__class__)
        
        # Ensure collection exists
        if collection_name not in self.collections:
            await self.create_table(model.__class__)
        
        collection = self.collections[collection_name]
        
        # Prepare data for insertion
        data = model.to_dict(exclude_none=False)
        
        # Generate primary key if needed
        pk_field = self.get_primary_key_field(model.__class__)
        if not data.get(pk_field):
            data[pk_field] = model.generate_id()
            setattr(model, pk_field, data[pk_field])
        
        # MongoDB uses _id as primary key, map from model's primary key
        if pk_field != '_id':
            data['_id'] = data[pk_field]
        
        try:
            result = await collection.insert_one(data)
            
            # Update model with generated ID if applicable
            if not getattr(model, pk_field):
                setattr(model, pk_field, str(result.inserted_id))
            
            return model
            
        except DuplicateKeyError as e:
            raise DuplicateError(f"Duplicate value for unique field: {str(e)}")
        except Exception as e:
            raise QueryError(f"Failed to insert document: {str(e)}")
    
    async def update(self, model: T) -> T:
        """Update an existing document."""
        self.validate_model(model)
        
        collection_name = self.get_collection_name(model.__class__)
        
        if collection_name not in self.collections:
            raise QueryError(f"Collection {collection_name} not found")
        
        collection = self.collections[collection_name]
        
        pk_field = self.get_primary_key_field(model.__class__)
        pk_value = getattr(model, pk_field)
        
        if not pk_value:
            raise ValidationError(f"Primary key field '{pk_field}' is required for update")
        
        # Prepare data for update (exclude primary key and _id)
        data = model.to_dict(exclude_none=False)
        update_data = {k: v for k, v in data.items() if k not in [pk_field, '_id']}
        
        # Determine query filter
        query_filter = {pk_field: pk_value} if pk_field != '_id' else {'_id': pk_value}
        
        try:
            result = await collection.update_one(
                query_filter,
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise NotFoundError(f"Document with {pk_field}={pk_value} not found")
            
            return model
            
        except NotFoundError:
            raise
        except Exception as e:
            raise QueryError(f"Failed to update document: {str(e)}")
    
    async def find_by_id(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Find a document by primary key."""
        collection_name = self.get_collection_name(model_class)
        
        if collection_name not in self.collections:
            return None
        
        collection = self.collections[collection_name]
        pk_field = self.get_primary_key_field(model_class)
        
        # Determine query filter
        query_filter = {pk_field: id_value} if pk_field != '_id' else {'_id': id_value}
        
        try:
            document = await collection.find_one(query_filter)
            
            if document:
                # Convert MongoDB document to model
                document = self._prepare_document_for_model(document, pk_field)
                return model_class.from_dict(document)
            
            return None
            
        except Exception as e:
            raise QueryError(f"Failed to find document: {str(e)}")
    
    async def find_many(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None
    ) -> List[T]:
        """Find multiple documents."""
        collection_name = self.get_collection_name(model_class)
        
        if collection_name not in self.collections:
            return []
        
        collection = self.collections[collection_name]
        pk_field = self.get_primary_key_field(model_class)
        
        # Build query
        query_filter = filters or {}
        
        try:
            cursor = collection.find(query_filter)
            
            # Apply sorting
            if order_by:
                sort_spec = []
                for field in order_by:
                    if field.startswith('-'):
                        sort_spec.append((field[1:], DESCENDING))
                    else:
                        sort_spec.append((field, ASCENDING))
                cursor = cursor.sort(sort_spec)
            
            # Apply pagination
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            # Convert documents to models
            models = []
            for doc in documents:
                doc = self._prepare_document_for_model(doc, pk_field)
                models.append(model_class.from_dict(doc))
            
            return models
            
        except Exception as e:
            raise QueryError(f"Failed to find documents: {str(e)}")
    
    async def delete_by_id(self, model_class: Type[T], id_value: Any) -> bool:
        """Delete a document by primary key."""
        collection_name = self.get_collection_name(model_class)
        
        if collection_name not in self.collections:
            return False
        
        collection = self.collections[collection_name]
        pk_field = self.get_primary_key_field(model_class)
        
        # Determine query filter
        query_filter = {pk_field: id_value} if pk_field != '_id' else {'_id': id_value}
        
        try:
            result = await collection.delete_one(query_filter)
            return result.deleted_count > 0
            
        except Exception as e:
            raise QueryError(f"Failed to delete document: {str(e)}")
    
    async def count(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count documents matching criteria."""
        collection_name = self.get_collection_name(model_class)
        
        if collection_name not in self.collections:
            return 0
        
        collection = self.collections[collection_name]
        query_filter = filters or {}
        
        try:
            return await collection.count_documents(query_filter)
        except Exception as e:
            raise QueryError(f"Failed to count documents: {str(e)}")
    
    async def exists(
        self, 
        model_class: Type[T], 
        filters: Dict[str, Any]
    ) -> bool:
        """Check if documents exist matching criteria."""
        count = await self.count(model_class, filters)
        return count > 0
    
    def _prepare_document_for_model(self, document: Dict[str, Any], pk_field: str) -> Dict[str, Any]:
        """Prepare MongoDB document for model creation."""
        # Map _id back to the model's primary key field
        if '_id' in document and pk_field != '_id':
            document[pk_field] = document['_id']
            del document['_id']
        
        return document
    
    # Synchronous method implementations
    
    def connect_sync(self) -> None:
        """Synchronous version of connect."""
        if not self._is_connected:
            asyncio.run(self.connect())
    
    def insert_sync(self, model: T) -> T:
        """Synchronous version of insert using sync client."""
        self.validate_model(model)
        
        collection_name = self.get_collection_name(model.__class__)
        
        # Ensure we have sync collection
        if collection_name not in self.sync_collections:
            # Create sync collection
            self.sync_collections[collection_name] = self.sync_database[collection_name]
        
        collection = self.sync_collections[collection_name]
        
        # Prepare data for insertion
        data = model.to_dict(exclude_none=False)
        
        # Generate primary key if needed
        pk_field = self.get_primary_key_field(model.__class__)
        if not data.get(pk_field):
            data[pk_field] = model.generate_id()
            setattr(model, pk_field, data[pk_field])
        
        # MongoDB uses _id as primary key, map from model's primary key
        if pk_field != '_id':
            data['_id'] = data[pk_field]
        
        try:
            result = collection.insert_one(data)
            
            # Update model with generated ID if applicable
            if not getattr(model, pk_field):
                setattr(model, pk_field, str(result.inserted_id))
            
            return model
            
        except DuplicateKeyError as e:
            raise DuplicateError(f"Duplicate value for unique field: {str(e)}")
        except Exception as e:
            raise QueryError(f"Failed to insert document: {str(e)}")
    
    def update_sync(self, model: T) -> T:
        """Synchronous version of update."""
        return asyncio.run(self.update(model))
    
    def find_by_id_sync(self, model_class: Type[T], id_value: Any) -> Optional[T]:
        """Synchronous version of find_by_id."""
        collection_name = self.get_collection_name(model_class)
        
        if collection_name not in self.sync_collections:
            return None
        
        collection = self.sync_collections[collection_name]
        pk_field = self.get_primary_key_field(model_class)
        
        # Determine query filter
        query_filter = {pk_field: id_value} if pk_field != '_id' else {'_id': id_value}
        
        try:
            document = collection.find_one(query_filter)
            
            if document:
                # Convert MongoDB document to model
                document = self._prepare_document_for_model(document, pk_field)
                return model_class.from_dict(document)
            
            return None
            
        except Exception as e:
            raise QueryError(f"Failed to find document: {str(e)}")
    
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