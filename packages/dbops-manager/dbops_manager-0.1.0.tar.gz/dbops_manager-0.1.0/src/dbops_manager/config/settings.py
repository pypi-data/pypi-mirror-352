"""Configuration management for database operations."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Settings:
    """Settings manager for database configuration."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize settings."""
        if not self._initialized:
            # Try to load .env file if it exists
            load_dotenv(override=True)
            self._initialized = True
            self._config = {}
    
    def configure(self, **kwargs):
        """
        Configure database settings directly.
        
        Args:
            **kwargs: Configuration key-value pairs
            
        Example:
            settings.configure(
                db_host='localhost',
                db_port=5432,
                db_username='user',
                db_password='pass',
                db_name='example'
            )
        """
        self._config.update(kwargs)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        # First check explicit configuration
        if key in self._config:
            return self._config[key]
        
        # Then check environment variables
        env_key = key.upper()
        return os.getenv(env_key, default)
    
    @property
    def db_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            'host': self.get('db_host', 'localhost'),
            'port': int(self.get('db_port', 5432)),
            'username': self.get('db_username', 'postgres'),
            'password': self.get('db_password', 'postgres'),
            'database': self.get('db_name', 'example'),
        }
    
    @property
    def test_db_config(self) -> Dict[str, Any]:
        """Get test database configuration dictionary."""
        config = self.db_config.copy()
        config['database'] = self.get('test_db_name', 'example_test')
        return config

# Global settings instance
settings = Settings()