"""
Norma Base Model

Provides the base class for all Norma ORM models with validation,
serialization, and metadata introspection capabilities.
"""

import re
import uuid
from dataclasses import dataclass, fields, asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, get_origin, get_args, Union
from uuid import uuid4

from ..exceptions import ValidationError
from .field import FieldConfig


T = TypeVar('T', bound='BaseModel')


@dataclass
class BaseModel:
    """
    Base class for all Norma ORM models.
    
    Provides:
    - Automatic validation based on field configuration
    - Serialization to/from dictionaries
    - Model metadata introspection
    - ID generation utilities
    
    Example:
        ```python
        @dataclass
        class User(BaseModel):
            id: str = Field(primary_key=True, default_factory=uuid4)
            name: str = Field(max_length=100)
            email: str = Field(unique=True)
            age: int = Field(default=0, min_value=0)
        ```
    """
    
    def __post_init__(self):
        """Automatically validate the model after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate all fields according to their configuration.
        
        Raises:
            ValidationError: If any field fails validation
        """
        for field_info in fields(self):
            field_name = field_info.name
            field_value = getattr(self, field_name)
            
            # Get Norma field configuration from metadata
            norma_config = field_info.metadata.get("norma_config")
            if not norma_config:
                continue
                
            self._validate_field(field_name, field_value, norma_config, field_info.type)
    
    def _validate_field(self, field_name: str, value: Any, config: FieldConfig, field_type: Type) -> None:
        """Validate a single field against its configuration."""
        
        # Check nullability
        if value is None:
            if not config.nullable and not config.primary_key:
                raise ValidationError(f"Field '{field_name}' cannot be None", field_name, value)
            return  # If None is allowed, skip other validations
        
        # Type validation
        self._validate_field_type(field_name, value, field_type)
        
        # String validations
        if isinstance(value, str):
            if config.min_length is not None and len(value) < config.min_length:
                raise ValidationError(
                    f"Field '{field_name}' must be at least {config.min_length} characters",
                    field_name, value
                )
            
            if config.max_length is not None and len(value) > config.max_length:
                raise ValidationError(
                    f"Field '{field_name}' must be at most {config.max_length} characters", 
                    field_name, value
                )
            
            if config.regex_pattern and not re.match(config.regex_pattern, value):
                raise ValidationError(
                    f"Field '{field_name}' does not match required pattern",
                    field_name, value
                )
        
        # Numeric validations
        if isinstance(value, (int, float)):
            if config.min_value is not None and value < config.min_value:
                raise ValidationError(
                    f"Field '{field_name}' must be at least {config.min_value}",
                    field_name, value
                )
            
            if config.max_value is not None and value > config.max_value:
                raise ValidationError(
                    f"Field '{field_name}' must be at most {config.max_value}",
                    field_name, value
                )
    
    def _validate_field_type(self, field_name: str, value: Any, expected_type: Type) -> None:
        """Validate field type more safely."""
        if value is None:
            return
        
        origin = get_origin(expected_type)
        
        # Handle Union types (like Optional)
        if origin is Union:
            args = get_args(expected_type)
            # For Optional types, check against the non-None type
            non_none_types = [arg for arg in args if arg is not type(None)]
            if non_none_types and not any(isinstance(value, t) for t in non_none_types if isinstance(t, type)):
                raise ValidationError(
                    f"Field '{field_name}' should be one of {non_none_types}, got {type(value)}",
                    field_name, value
                )
        elif isinstance(expected_type, type) and not isinstance(value, expected_type):
            raise ValidationError(
                f"Field '{field_name}' should be {expected_type.__name__}, got {type(value).__name__}",
                field_name, value
            )
    
    def to_dict(self, exclude_none: bool = True, exclude_private: bool = True) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.
        
        Args:
            exclude_none: Whether to exclude None values
            exclude_private: Whether to exclude fields starting with underscore
            
        Returns:
            Dictionary representation of the model
        """
        result = asdict(self)
        
        if exclude_none:
            result = {k: v for k, v in result.items() if v is not None}
        
        if exclude_private:
            result = {k: v for k, v in result.items() if not k.startswith('_')}
        
        return result
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing field values
            
        Returns:
            New model instance
        """
        # Filter data to only include fields that exist in the model
        model_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in model_fields}
        
        return cls(**filtered_data)
    
    def update(self, **kwargs) -> None:
        """
        Update model fields with validation.
        
        Args:
            **kwargs: Field values to update
        """
        # Get valid field names
        valid_fields = {f.name for f in fields(self)}
        
        for key, value in kwargs.items():
            if key not in valid_fields:
                raise ValidationError(f"Unknown field '{key}' for {self.__class__.__name__}")
            setattr(self, key, value)
        
        # Re-validate after updates
        self.validate()
    
    @classmethod
    def get_field_config(cls, field_name: str) -> Optional[FieldConfig]:
        """Get the Norma configuration for a specific field."""
        for field_info in fields(cls):
            if field_info.name == field_name:
                return field_info.metadata.get("norma_config")
        return None
    
    @classmethod
    def get_primary_key_field(cls) -> Optional[str]:
        """Get the name of the primary key field."""
        for field_info in fields(cls):
            config = field_info.metadata.get("norma_config")
            if config and config.primary_key:
                return field_info.name
        return None
    
    @classmethod
    def get_unique_fields(cls) -> List[str]:
        """Get names of all unique fields."""
        unique_fields = []
        for field_info in fields(cls):
            config = field_info.metadata.get("norma_config")
            if config and (config.unique or config.primary_key):
                unique_fields.append(field_info.name)
        return unique_fields
    
    @classmethod
    def get_indexed_fields(cls) -> List[str]:
        """Get names of all indexed fields."""
        indexed_fields = []
        for field_info in fields(cls):
            config = field_info.metadata.get("norma_config")
            if config and (config.index or config.unique or config.primary_key):
                indexed_fields.append(field_info.name)
        return indexed_fields
    
    @classmethod
    def get_relationship_fields(cls) -> Dict[str, FieldConfig]:
        """Get all fields that define relationships."""
        relationships = {}
        for field_info in fields(cls):
            config = field_info.metadata.get("norma_config")
            if config and config.relationship:
                relationships[field_info.name] = config
        return relationships
    
    @staticmethod
    def generate_id() -> str:
        """Generate a new unique identifier."""
        return uuid4().hex
    
    def get_primary_key_value(self) -> Any:
        """Get the value of the primary key field."""
        pk_field = self.get_primary_key_field()
        if pk_field:
            return getattr(self, pk_field)
        return None
    
    def is_persisted(self) -> bool:
        """Check if this model has been saved to the database."""
        pk_value = self.get_primary_key_value()
        return pk_value is not None
    
    def __str__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        fields_str = ', '.join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{class_name}({fields_str})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return self.__str__()


def model_metadata(model_class: Type[BaseModel]) -> Dict[str, Any]:
    """
    Extract metadata from a Norma model class.
    
    Args:
        model_class: The model class to analyze
        
    Returns:
        Dictionary containing model metadata
    """
    if not is_dataclass(model_class) or not issubclass(model_class, BaseModel):
        raise ValueError("Class must be a Norma BaseModel dataclass")
    
    metadata = {
        "name": model_class.__name__,
        "fields": {},
        "primary_key": model_class.get_primary_key_field(),
        "unique_fields": model_class.get_unique_fields(),
        "indexed_fields": model_class.get_indexed_fields(),
        "relationships": model_class.get_relationship_fields(),
    }
    
    for field_info in fields(model_class):
        field_name = field_info.name
        config = field_info.metadata.get("norma_config")
        
        metadata["fields"][field_name] = {
            "type": field_info.type,
            "config": config,
            "has_default": field_info.default != field_info.default_factory,
        }
    
    return metadata 