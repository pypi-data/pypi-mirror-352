"""
Norma ORM Exception Classes

Custom exceptions for better error handling and debugging.
"""

from typing import Any, Dict, Optional


class NormaError(Exception):
    """Base exception class for all Norma ORM errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ValidationError(NormaError):
    """Raised when model validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)
        self.field = field
        self.value = value


class NotFoundError(NormaError):
    """Raised when a requested entity is not found."""
    
    def __init__(self, message: str, model: Optional[str] = None, query: Optional[Dict[str, Any]] = None):
        details = {}
        if model:
            details["model"] = model
        if query:
            details["query"] = query
        super().__init__(message, details)
        self.model = model
        self.query = query


class ConnectionError(NormaError):
    """Raised when database connection fails."""
    
    def __init__(self, message: str, database_url: Optional[str] = None):
        details = {}
        if database_url:
            # Don't include sensitive connection info in details
            details["database_type"] = database_url.split("://")[0] if "://" in database_url else "unknown"
        super().__init__(message, details)


class DuplicateError(NormaError):
    """Raised when attempting to create a duplicate record."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)
        self.field = field
        self.value = value


class ConfigurationError(NormaError):
    """Raised when Norma is misconfigured."""
    pass


class QueryError(NormaError):
    """Raised when a database query fails."""
    
    def __init__(self, message: str, query: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        details = {}
        if query:
            details["query"] = query
        if params:
            details["params"] = params
        super().__init__(message, details)
        self.query = query
        self.params = params


class SchemaGenerationError(NormaError):
    """Raised when schema generation fails."""
    
    def __init__(self, message: str, model: Optional[str] = None):
        details = {}
        if model:
            details["model"] = model
        super().__init__(message, details)
        self.model = model 