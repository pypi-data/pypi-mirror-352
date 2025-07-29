# exceptions.py

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass

class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass
