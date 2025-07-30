"""PostgreSQL implementation of database operations."""

from typing import List, Dict, Any, Type
from sqlalchemy.ext.declarative import DeclarativeMeta
from dbops_manager.managers.db_manager import DatabaseManager
from dbops_manager.base.operations import DatabaseOperations

class PostgresOperations(DatabaseOperations):
    """PostgreSQL implementation of database operations."""

    def __init__(self, model_class: Type[DeclarativeMeta]):
        """
        Initialize PostgreSQL operations with database manager and model class.
        
        Args:
            model_class: SQLAlchemy model class to use for database operations
        """
        self.db = DatabaseManager()
        self.model = model_class

    def create_users(self, users_data: List[Dict[str, Any]]) -> None:
        """
        Create multiple users in the database.
        
        Args:
            users_data: List of dictionaries containing user data
        """
        try:
            for user_data in users_data:
                user = self.db.create_user(self.model, user_data)
                if user:
                    print(f"Created user: {user}")
                else:
                    print(f"Failed to create user with data: {user_data}")
        except Exception as e:
            print(f"Error in create_users: {str(e)}")

    def get_user_by_id(self, user_id: int) -> None:
        """
        Retrieve and display user information by ID.
        
        Args:
            user_id: ID of the user to retrieve
        """
        try:
            user = self.db.get_user(self.model, user_id)
            if user:
                print(f"Found user: {user}")
            else:
                print(f"No user found with ID: {user_id}")
        except Exception as e:
            print(f"Error in get_user_by_id: {str(e)}")

    def list_all_users(self) -> None:
        """List all users in the database."""
        try:
            users = self.db.get_all_users(self.model)
            if users:
                print("\nAll users:")
                for user in users:
                    print(f"User {user.id}: {user.name} - {user.email}")
            else:
                print("No users found in the database")
        except Exception as e:
            print(f"Error in list_all_users: {str(e)}")

    def update_user_info(self, user_id: int, update_data: Dict[str, Any]) -> None:
        """
        Update user information.
        
        Args:
            user_id: ID of the user to update
            update_data: Dictionary containing fields to update
        """
        try:
            updated_user = self.db.update_user(self.model, user_id, update_data)
            if updated_user:
                print(f"Updated user: {updated_user}")
            else:
                print(f"Failed to update user with ID: {user_id}")
        except Exception as e:
            print(f"Error in update_user_info: {str(e)}")

    def delete_user_by_id(self, user_id: int) -> None:
        """
        Delete a user by ID.
        
        Args:
            user_id: ID of the user to delete
        """
        try:
            if self.db.delete_user(self.model, user_id):
                print(f"Successfully deleted user with ID: {user_id}")
            else:
                print(f"Failed to delete user with ID: {user_id}")
        except Exception as e:
            print(f"Error in delete_user_by_id: {str(e)}")

