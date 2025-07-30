"""MongoDB implementation of database operations."""

from typing import List, Dict, Any
from base import DatabaseOperations
from pymongo import MongoClient
from config.config import Config

class MongoOperations(DatabaseOperations):
    """MongoDB implementation of database operations."""

    def __init__(self):
        """Initialize MongoDB connection."""
        try:
            config = Config()
            self.client = MongoClient(
                host=config.DB_HOST,
                port=config.DB_PORT,
                username=config.DB_USERNAME,
                password=config.DB_PASSWORD
            )
            self.db = self.client[config.DB_NAME]
            self.users = self.db.users
        except Exception as e:
            raise Exception(f"Failed to initialize MongoDB connection: {str(e)}")

    def create_users(self, users_data: List[Dict[str, Any]]) -> None:
        """
        Create multiple users in the database.
        
        Args:
            users_data: List of dictionaries containing user data
        """
        try:
            for user_data in users_data:
                result = self.users.insert_one(user_data)
                if result.inserted_id:
                    user = self.users.find_one({"_id": result.inserted_id})
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
            user = self.users.find_one({"_id": user_id})
            if user:
                print(f"Found user: {user}")
            else:
                print(f"No user found with ID: {user_id}")
        except Exception as e:
            print(f"Error in get_user_by_id: {str(e)}")

    def list_all_users(self) -> None:
        """List all users in the database."""
        try:
            users = list(self.users.find())
            if users:
                print("\nAll users:")
                for user in users:
                    print(f"User {user['_id']}: {user.get('name')} - {user.get('email')}")
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
            result = self.users.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            if result.modified_count:
                user = self.users.find_one({"_id": user_id})
                print(f"Updated user: {user}")
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
            result = self.users.delete_one({"_id": user_id})
            if result.deleted_count:
                print(f"Successfully deleted user with ID: {user_id}")
            else:
                print(f"Failed to delete user with ID: {user_id}")
        except Exception as e:
            print(f"Error in delete_user_by_id: {str(e)}")

    def __del__(self):
        """Cleanup MongoDB connection on object destruction."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            print(f"Error disconnecting from MongoDB: {str(e)}")

# Create a global instance
mongo_db = MongoOperations() 