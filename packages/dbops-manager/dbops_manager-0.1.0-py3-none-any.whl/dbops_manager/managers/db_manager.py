"""Database manager implementation."""

from typing import Optional, List, Dict, Any, Type
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from dbops_manager.config.settings import settings

class DatabaseManager:
    """Manages database connections and operations."""
    
    _instance = None
    _session = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection."""
        config = settings.db_config
        connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get or create a database session."""
        if not self._session:
            self._session = self.SessionLocal()
        return self._session

    def create_user(self, model: Type[DeclarativeMeta], user_data: Dict[str, Any]) -> Optional[DeclarativeMeta]:
        """Create a new user."""
        session = self.get_session()
        try:
            user = model(**user_data)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            print(f"Error creating user: {str(e)}")
            return None

    def get_user(self, model: Type[DeclarativeMeta], user_id: int) -> Optional[DeclarativeMeta]:
        """Get user by ID."""
        session = self.get_session()
        return session.query(model).filter(model.id == user_id).first()

    def get_all_users(self, model: Type[DeclarativeMeta]) -> List[DeclarativeMeta]:
        """Get all users."""
        session = self.get_session()
        return session.query(model).all()

    def update_user(self, model: Type[DeclarativeMeta], user_id: int, update_data: Dict[str, Any]) -> Optional[DeclarativeMeta]:
        """Update user information."""
        session = self.get_session()
        try:
            user = session.query(model).filter(model.id == user_id).first()
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                session.commit()
                session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            print(f"Error updating user: {str(e)}")
            return None

    def delete_user(self, model: Type[DeclarativeMeta], user_id: int) -> bool:
        """Delete user by ID."""
        session = self.get_session()
        try:
            user = session.query(model).filter(model.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting user: {str(e)}")
            return False

    def __del__(self):
        """Clean up database session."""
        if self._session:
            self._session.close()
            self._session = None 