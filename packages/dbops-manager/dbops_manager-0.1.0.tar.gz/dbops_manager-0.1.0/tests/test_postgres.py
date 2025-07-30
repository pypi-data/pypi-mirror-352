"""Test cases for PostgreSQL provider."""

import unittest
from db.db_manager import DatabaseManager
from models import User

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        try:
            cls.db = DatabaseManager()
        except Exception as e:
            raise Exception(f"Failed to set up database connection: {str(e)}")

    def setUp(self):
        """Set up test case."""
        try:
            # Clear the users table before each test
            session = self.db.provider.Session()
            session.query(User).delete()
            session.commit()
            session.close()
        except Exception as e:
            self.fail(f"Failed to clear database before test: {str(e)}")

    def test_create_user(self):
        """Test user creation."""
        try:
            user_data = {"name": "Test User", "email": "test@example.com"}
            user = self.db.create_user(user_data)
            
            self.assertIsNotNone(user)
            self.assertIsNotNone(user.id)
            self.assertEqual(user.name, user_data["name"])
            self.assertEqual(user.email, user_data["email"])
        except Exception as e:
            self.fail(f"Test create user failed: {str(e)}")

    def test_get_user(self):
        """Test user retrieval."""
        try:
            # Create a test user
            user_data = {"name": "Read Test", "email": "read@example.com"}
            created_user = self.db.create_user(user_data)
            
            # Read the user
            read_user = self.db.get_user(created_user.id)
            
            self.assertIsNotNone(read_user)
            self.assertEqual(read_user.name, user_data["name"])
            self.assertEqual(read_user.email, user_data["email"])
        except Exception as e:
            self.fail(f"Test get user failed: {str(e)}")

    def test_get_nonexistent_user(self):
        """Test retrieval of non-existent user."""
        try:
            user = self.db.get_user(999)
            self.assertIsNone(user)
        except Exception as e:
            self.fail(f"Test get nonexistent user failed: {str(e)}")

    def test_update_user(self):
        """Test user update."""
        try:
            # Create a test user
            user_data = {"name": "Update Test", "email": "update@example.com"}
            created_user = self.db.create_user(user_data)
            
            # Update the user
            updated_data = {"name": "Updated Name"}
            updated_user = self.db.update_user(created_user.id, updated_data)
            
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user.name, updated_data["name"])
            self.assertEqual(updated_user.email, user_data["email"])
        except Exception as e:
            self.fail(f"Test update user failed: {str(e)}")

    def test_delete_user(self):
        """Test user deletion."""
        try:
            # Create a test user
            user_data = {"name": "Delete Test", "email": "delete@example.com"}
            created_user = self.db.create_user(user_data)
            
            # Delete the user
            result = self.db.delete_user(created_user.id)
            self.assertTrue(result)
            
            # Try to read the deleted user
            deleted_user = self.db.get_user(created_user.id)
            self.assertIsNone(deleted_user)
        except Exception as e:
            self.fail(f"Test delete user failed: {str(e)}")

    def test_get_all_users(self):
        """Test retrieving all users."""
        try:
            # Create multiple test users
            user_data_list = [
                {"name": "User 1", "email": "user1@example.com"},
                {"name": "User 2", "email": "user2@example.com"},
                {"name": "User 3", "email": "user3@example.com"}
            ]
            
            for user_data in user_data_list:
                self.db.create_user(user_data)
            
            # Get all users
            users = self.db.get_all_users()
            
            self.assertEqual(len(users), len(user_data_list))
            for user, data in zip(sorted(users, key=lambda x: x.email), user_data_list):
                self.assertEqual(user.name, data["name"])
                self.assertEqual(user.email, data["email"])
        except Exception as e:
            self.fail(f"Test get all users failed: {str(e)}")

if __name__ == '__main__':
    unittest.main() 