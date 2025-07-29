"""
Norma Schema Generator

Automatically generates Pydantic schemas from Norma dataclass models
for input validation and output serialization.
"""

import inspect
from typing import Any, Dict, List, Optional, Type, get_origin, get_args, Union
from dataclasses import fields, is_dataclass
from datetime import datetime

try:
    from pydantic import BaseModel as PydanticBaseModel, Field as PydanticField, create_model
    from pydantic.fields import FieldInfo
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    PydanticBaseModel = object
    PydanticField = None
    FieldInfo = None

from ..core.base_model import BaseModel
from ..core.field import FieldConfig
from ..exceptions import SchemaGenerationError


class SchemaGenerator:
    """
    Generates Pydantic schemas from Norma dataclass models.
    
    Creates Create, Read, Update schemas automatically with proper
    validation rules based on field configurations.
    """
    
    def __init__(self):
        """Initialize schema generator."""
        if not PYDANTIC_AVAILABLE:
            raise SchemaGenerationError(
                "Pydantic is not available. Install with: pip install pydantic>=2.0.0"
            )
        
        self._schema_cache: Dict[str, Type[PydanticBaseModel]] = {}
    
    def generate_schemas(self, model_class: Type[BaseModel]) -> Dict[str, Type[PydanticBaseModel]]:
        """
        Generate all schemas for a model class.
        
        Args:
            model_class: The Norma model class to generate schemas for
            
        Returns:
            Dictionary containing 'create', 'read', 'update' schemas
        """
        if not is_dataclass(model_class) or not issubclass(model_class, BaseModel):
            raise SchemaGenerationError(
                f"{model_class.__name__} must be a Norma BaseModel dataclass"
            )
        
        model_name = model_class.__name__
        
        schemas = {
            'create': self.generate_create_schema(model_class),
            'read': self.generate_read_schema(model_class),
            'update': self.generate_update_schema(model_class),
        }
        
        return schemas
    
    def generate_create_schema(self, model_class: Type[BaseModel]) -> Type[PydanticBaseModel]:
        """
        Generate a Create schema for input validation.
        
        Excludes auto-generated fields like primary keys with defaults.
        """
        cache_key = f"{model_class.__name__}_Create"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        model_name = f"{model_class.__name__}Create"
        field_definitions = {}
        
        for field_info in fields(model_class):
            field_name = field_info.name
            field_type = field_info.type
            config = field_info.metadata.get("norma_config")
            
            # Skip auto-generated primary keys for create schema
            if config and config.primary_key and (config.default_factory or config.default):
                continue
            
            # Convert to Pydantic field
            pydantic_field = self._create_pydantic_field(field_type, config, for_create=True)
            field_definitions[field_name] = (field_type, pydantic_field)
        
        # Create Pydantic model
        schema_class = create_model(model_name, **field_definitions)
        self._schema_cache[cache_key] = schema_class
        
        return schema_class
    
    def generate_read_schema(self, model_class: Type[BaseModel]) -> Type[PydanticBaseModel]:
        """
        Generate a Read schema for output serialization.
        
        Includes all fields with their current values.
        """
        cache_key = f"{model_class.__name__}_Read"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        model_name = f"{model_class.__name__}Read"
        field_definitions = {}
        
        for field_info in fields(model_class):
            field_name = field_info.name
            field_type = field_info.type
            config = field_info.metadata.get("norma_config")
            
            # Include all fields in read schema
            pydantic_field = self._create_pydantic_field(field_type, config, for_read=True)
            field_definitions[field_name] = (field_type, pydantic_field)
        
        # Create Pydantic model
        schema_class = create_model(model_name, **field_definitions)
        self._schema_cache[cache_key] = schema_class
        
        return schema_class
    
    def generate_update_schema(self, model_class: Type[BaseModel]) -> Type[PydanticBaseModel]:
        """
        Generate an Update schema for partial updates.
        
        Makes most fields optional except for the primary key.
        """
        cache_key = f"{model_class.__name__}_Update"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        model_name = f"{model_class.__name__}Update"
        field_definitions = {}
        
        pk_field = model_class.get_primary_key_field()
        
        for field_info in fields(model_class):
            field_name = field_info.name
            field_type = field_info.type
            config = field_info.metadata.get("norma_config")
            
            # Primary key is required for updates
            if field_name == pk_field:
                pydantic_field = self._create_pydantic_field(field_type, config, for_update=True)
                field_definitions[field_name] = (field_type, pydantic_field)
            else:
                # Make other fields optional for partial updates
                optional_type = Optional[field_type]
                pydantic_field = self._create_pydantic_field(
                    optional_type, config, for_update=True, make_optional=True
                )
                field_definitions[field_name] = (optional_type, pydantic_field)
        
        # Create Pydantic model
        schema_class = create_model(model_name, **field_definitions)
        self._schema_cache[cache_key] = schema_class
        
        return schema_class
    
    def _create_pydantic_field(
        self, 
        field_type: Type, 
        config: Optional[FieldConfig], 
        for_create: bool = False,
        for_read: bool = False,
        for_update: bool = False,
        make_optional: bool = False
    ) -> FieldInfo:
        """Create a Pydantic field from Norma field configuration."""
        
        # Base field arguments
        field_kwargs = {}
        
        if config:
            # Description
            if config.description:
                field_kwargs['description'] = config.description
            
            # Default values
            if not make_optional:
                if config.default is not None:
                    field_kwargs['default'] = config.default
                elif config.default_factory:
                    field_kwargs['default_factory'] = config.default_factory
                elif not config.nullable and not for_read:
                    # Field is required
                    pass
                else:
                    field_kwargs['default'] = None
            else:
                # For optional fields in update schema
                field_kwargs['default'] = None
            
            # Validation constraints
            if isinstance(field_type, type) and issubclass(field_type, str):
                if config.min_length is not None:
                    field_kwargs['min_length'] = config.min_length
                if config.max_length is not None:
                    field_kwargs['max_length'] = config.max_length
                if config.regex_pattern:
                    field_kwargs['pattern'] = config.regex_pattern
            
            elif isinstance(field_type, type) and issubclass(field_type, (int, float)):
                if config.min_value is not None:
                    field_kwargs['ge'] = config.min_value  # greater than or equal
                if config.max_value is not None:
                    field_kwargs['le'] = config.max_value  # less than or equal
        
        return PydanticField(**field_kwargs)
    
    def model_to_schema_dict(
        self, 
        model: BaseModel, 
        schema_type: str = "read"
    ) -> Dict[str, Any]:
        """
        Convert a model instance to a dictionary using the appropriate schema.
        
        Args:
            model: The model instance to convert
            schema_type: Type of schema to use ('create', 'read', 'update')
            
        Returns:
            Dictionary representation validated by the schema
        """
        schemas = self.generate_schemas(model.__class__)
        schema_class = schemas.get(schema_type)
        
        if not schema_class:
            raise SchemaGenerationError(f"Schema type '{schema_type}' not found")
        
        # Convert model to dict and validate with schema
        model_dict = model.to_dict()
        
        try:
            schema_instance = schema_class(**model_dict)
            return schema_instance.model_dump()
        except Exception as e:
            raise SchemaGenerationError(
                f"Failed to convert model to {schema_type} schema: {str(e)}"
            )
    
    def schema_dict_to_model(
        self, 
        data: Dict[str, Any], 
        model_class: Type[BaseModel],
        schema_type: str = "create"
    ) -> BaseModel:
        """
        Convert a schema dictionary to a model instance.
        
        Args:
            data: Dictionary data from schema
            model_class: The model class to create
            schema_type: Type of schema used ('create', 'read', 'update')
            
        Returns:
            Model instance created from the data
        """
        schemas = self.generate_schemas(model_class)
        schema_class = schemas.get(schema_type)
        
        if not schema_class:
            raise SchemaGenerationError(f"Schema type '{schema_type}' not found")
        
        try:
            # Validate data with schema first
            schema_instance = schema_class(**data)
            validated_data = schema_instance.model_dump(exclude_none=True)
            
            # Create model instance
            return model_class.from_dict(validated_data)
        except Exception as e:
            raise SchemaGenerationError(
                f"Failed to convert {schema_type} schema to model: {str(e)}"
            )
    
    def clear_cache(self) -> None:
        """Clear the schema cache."""
        self._schema_cache.clear()
    
    def get_cached_schemas(self) -> Dict[str, Type[PydanticBaseModel]]:
        """Get all cached schemas."""
        return self._schema_cache.copy()


# Global schema generator instance
_generator = None


def get_schema_generator() -> SchemaGenerator:
    """Get the global schema generator instance."""
    global _generator
    if _generator is None:
        _generator = SchemaGenerator()
    return _generator


def generate_schemas(model_class: Type[BaseModel]) -> Dict[str, Type[PydanticBaseModel]]:
    """
    Convenience function to generate schemas for a model class.
    
    Args:
        model_class: The Norma model class
        
    Returns:
        Dictionary containing generated schemas
    """
    return get_schema_generator().generate_schemas(model_class)


def create_schema(model_class: Type[BaseModel]) -> Type[PydanticBaseModel]:
    """Generate a Create schema for a model class."""
    return get_schema_generator().generate_create_schema(model_class)


def read_schema(model_class: Type[BaseModel]) -> Type[PydanticBaseModel]:
    """Generate a Read schema for a model class."""
    return get_schema_generator().generate_read_schema(model_class)


def update_schema(model_class: Type[BaseModel]) -> Type[PydanticBaseModel]:
    """Generate an Update schema for a model class."""
    return get_schema_generator().generate_update_schema(model_class) 