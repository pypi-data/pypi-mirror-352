"""
Norma Core Components

This package contains the core components of Norma ORM.
"""

from .base_model import BaseModel, model_metadata
from .field import Field, FieldConfig, Relationship, OneToOne, OneToMany, ManyToOne, ManyToMany
from .client import NormaClient, ModelClient

__all__ = [
    "BaseModel",
    "model_metadata",
    "Field",
    "FieldConfig", 
    "Relationship",
    "OneToOne",
    "OneToMany",
    "ManyToOne", 
    "ManyToMany",
    "NormaClient",
    "ModelClient",
] 