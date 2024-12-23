"""
User database model.
Defines the structure of the users table in the database.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.context import CryptContext

from ..db.base import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    User model for storing user information and authentication details.

    Attributes:
        id (int): Primary key
        username (str): Unique username
        hashed_password (str): Bcrypt hashed password
        tasks (relationship): Relationship to associated Task objects
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relationship with Task model (will be defined later)
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

    @hybrid_property
    def password(self):
        """Prevent password from being read."""
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password: str):
        """Hash password on set."""
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against hash.

        Args:
            password (str): Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(password, self.hashed_password) 
