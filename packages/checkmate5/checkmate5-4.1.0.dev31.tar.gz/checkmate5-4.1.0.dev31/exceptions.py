class ConfigurationError(Exception):
    """Exception raised for configuration-related errors.
    
    Attributes:
        message -- explanation of the error
        config -- configuration that caused the error (optional)
    """

    def __init__(self, message: str, config: dict = None) -> None:
        self.message = message
        self.config = config
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.config:
            return f"{self.message} (Config: {self.config})"
        return self.message

class SQLBackend:
    def __init__(self, *args, **kwargs):
        # ... existing code ...
        pass

    def create_tables(self):
        """
        Creates necessary database tables if they don't exist.
        """
        try:
            # Create tables for storing analysis results
            with self.engine.connect() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id SERIAL PRIMARY KEY,
                        hash TEXT,
                        analyzer TEXT,
                        line INTEGER,
                        file TEXT,
                        severity TEXT,
                        code TEXT,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        except Exception as e:
            raise DatabaseError(f"Failed to create tables: {str(e)}")

class DatabaseError(Exception):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)