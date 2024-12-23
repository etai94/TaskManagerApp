# app/schemas/task.py
"""
Pydantic schemas for task data validation and serialization.
"""
from pydantic import BaseModel, validator

class TaskBase(BaseModel):
    """Base task schema with common attributes."""
    description: str

    @validator('description')
    def description_not_empty(cls, v):
        """Validate description is not empty."""
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    description: str | None = None
    completed: bool | None = None

class Task(TaskBase):
    """Schema for task responses."""
    id: int
    completed: bool
    user_id: int

    class Config:
        """Pydantic configuration."""
        orm_mode = True
