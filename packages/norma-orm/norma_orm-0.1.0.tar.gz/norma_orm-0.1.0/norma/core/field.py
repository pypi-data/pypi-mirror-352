"""
Norma Field Definition

Provides field configuration for dataclass models including validation,
indexing, relationships, and database-specific options.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Type, Union, get_origin, get_args
from enum import Enum


class RelationType(Enum):
    """Supported relationship types."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


@dataclass
class Relationship:
    """Defines a relationship between models."""
    
    target_model: str
    relation_type: RelationType
    foreign_key: Optional[str] = None
    back_ref: Optional[str] = None
    cascade_delete: bool = False
    lazy_load: bool = True


@dataclass 
class FieldConfig:
    """Configuration for a model field."""
    
    # Basic field properties
    default: Any = None
    default_factory: Optional[Callable[[], Any]] = None
    
    # Database constraints
    primary_key: bool = False
    unique: bool = False
    index: bool = False
    nullable: bool = True
    
    # Validation
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    regex_pattern: Optional[str] = None
    
    # Relationships
    relationship: Optional[Relationship] = None
    
    # Database-specific options
    db_column_name: Optional[str] = None
    db_type: Optional[str] = None
    db_options: Optional[Dict[str, Any]] = None
    
    # Documentation
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate field configuration after initialization."""
        if self.primary_key and self.nullable:
            self.nullable = False  # Primary keys cannot be nullable
        
        if self.default is not None and self.default_factory is not None:
            raise ValueError("Cannot specify both default and default_factory")


def Field(
    default: Any = None,
    default_factory: Optional[Callable[[], Any]] = None,
    primary_key: bool = False,
    unique: bool = False,
    index: bool = False,
    nullable: bool = True,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    regex_pattern: Optional[str] = None,
    relationship: Optional[Relationship] = None,
    db_column_name: Optional[str] = None,
    db_type: Optional[str] = None,
    db_options: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
) -> Any:
    """
    Create a field with configuration for dataclass models.
    
    Args:
        default: Default value for the field
        default_factory: Factory function to generate default values
        primary_key: Whether this field is a primary key
        unique: Whether this field must be unique
        index: Whether to create a database index on this field
        nullable: Whether this field can be None
        min_length: Minimum length for string fields
        max_length: Maximum length for string fields
        min_value: Minimum value for numeric fields
        max_value: Maximum value for numeric fields
        regex_pattern: Regex pattern for string validation
        relationship: Relationship configuration
        db_column_name: Custom database column name
        db_type: Custom database type
        db_options: Additional database-specific options
        description: Field description for documentation
    
    Returns:
        A dataclass field with Norma configuration
    
    Example:
        ```python
        @dataclass
        class User(BaseModel):
            id: str = Field(primary_key=True, default_factory=uuid4)
            email: str = Field(unique=True, max_length=255)
            age: int = Field(default=0, min_value=0, max_value=150)
            name: str = Field(index=True, max_length=100)
        ```
    """
    config = FieldConfig(
        default=default,
        default_factory=default_factory,
        primary_key=primary_key,
        unique=unique,
        index=index,
        nullable=nullable,
        min_length=min_length,
        max_length=max_length,
        min_value=min_value,
        max_value=max_value,
        regex_pattern=regex_pattern,
        relationship=relationship,
        db_column_name=db_column_name,
        db_type=db_type,
        db_options=db_options or {},
        description=description,
    )
    
    # Determine the actual default value for the dataclass field
    if default_factory is not None:
        dataclass_default = field(default_factory=default_factory)
    elif default is not None:
        dataclass_default = field(default=default)
    else:
        dataclass_default = field()
    
    # Store the Norma configuration in the field metadata
    dataclass_default.metadata = {"norma_config": config}
    
    return dataclass_default


def OneToOne(target_model: str, foreign_key: Optional[str] = None, 
             back_ref: Optional[str] = None, cascade_delete: bool = False) -> Relationship:
    """Create a one-to-one relationship."""
    return Relationship(
        target_model=target_model,
        relation_type=RelationType.ONE_TO_ONE,
        foreign_key=foreign_key,
        back_ref=back_ref,
        cascade_delete=cascade_delete,
    )


def OneToMany(target_model: str, foreign_key: Optional[str] = None,
              back_ref: Optional[str] = None, cascade_delete: bool = False) -> Relationship:
    """Create a one-to-many relationship."""
    return Relationship(
        target_model=target_model,
        relation_type=RelationType.ONE_TO_MANY,
        foreign_key=foreign_key,
        back_ref=back_ref,
        cascade_delete=cascade_delete,
    )


def ManyToOne(target_model: str, foreign_key: Optional[str] = None,
              back_ref: Optional[str] = None) -> Relationship:
    """Create a many-to-one relationship."""
    return Relationship(
        target_model=target_model,
        relation_type=RelationType.MANY_TO_ONE,
        foreign_key=foreign_key,
        back_ref=back_ref,
        cascade_delete=False,  # Typically don't cascade delete on many-to-one
    )


def ManyToMany(target_model: str, back_ref: Optional[str] = None) -> Relationship:
    """Create a many-to-many relationship."""
    return Relationship(
        target_model=target_model,
        relation_type=RelationType.MANY_TO_MANY,
        back_ref=back_ref,
        cascade_delete=False,  # Typically don't cascade delete on many-to-many
    ) 