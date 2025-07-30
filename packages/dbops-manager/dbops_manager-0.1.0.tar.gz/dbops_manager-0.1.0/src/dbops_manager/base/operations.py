"""Base interface for database operations."""

from typing import List, Dict, Any
from abc import ABC, abstractmethod

class DatabaseOperations(ABC):
    """Abstract base class for database operations."""

    @abstractmethod
    def create_users(self, users_data: List[Dict[str, Any]]) -> None:
        """Create multiple users in the database."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> None:
        """Retrieve user by ID."""
        pass

    @abstractmethod
    def list_all_users(self) -> None:
        """List all users in the database."""
        pass

    @abstractmethod
    def update_user_info(self, user_id: int, update_data: Dict[str, Any]) -> None:
        """Update user information."""
        pass

    @abstractmethod
    def delete_user_by_id(self, user_id: int) -> None:
        """Delete a user by ID."""
        pass 