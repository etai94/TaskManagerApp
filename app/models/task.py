"""
Task database model.
Defines the structure of the tasks table in the database.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base import Base


class Task(Base):
    """
    Task model for storing task information.

    Attributes:
        id (int): Primary key
        description (str): Task description
        completed (bool): Task completion status
        user_id (int): Foreign key to users table
        owner (relationship): Relationship to User object
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship with User model
    owner = relationship("User", back_populates="tasks")
