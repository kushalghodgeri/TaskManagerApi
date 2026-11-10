from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base schema for task attributes."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Task title (1-100 characters)",
        examples=["Complete project documentation"],
    )
    description: str | None = Field(
        default=None,
        description="Detailed description of the task",
        examples=["Write comprehensive API docs and usage guides"],
    )
    status: TaskStatus = Field(
        default=TaskStatus.todo,
        description="Current task status: todo, in_progress, or done",
        examples=[TaskStatus.todo],
    )
    priority: TaskPriority = Field(
        default=TaskPriority.medium,
        description="Task priority level: low, medium, or high",
        examples=[TaskPriority.medium],
    )
    due_date: datetime | None = Field(
        default=None,
        description="Task due date with timezone",
        examples=["2026-12-31T23:59:59Z"],
    )


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Build REST API",
                "description": "Implement authentication and CRUD endpoints",
                "status": "todo",
                "priority": "high",
                "due_date": "2026-12-31T23:59:59Z",
            }
        }
    )


class TaskUpdate(BaseModel):
    """Schema for partially updating an existing task (all fields optional)."""
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Task title (1-100 characters)",
        examples=["Build REST API v2"],
    )
    description: str | None = Field(
        default=None,
        description="Detailed description of the task",
        examples=["Updated requirements"],
    )
    status: TaskStatus | None = Field(
        default=None,
        description="Current task status: todo, in_progress, or done",
        examples=[TaskStatus.in_progress],
    )
    priority: TaskPriority | None = Field(
        default=None,
        description="Task priority level: low, medium, or high",
        examples=[TaskPriority.high],
    )
    due_date: datetime | None = Field(
        default=None,
        description="Task due date with timezone",
        examples=["2026-12-31T23:59:59Z"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Refactor authentication",
                "status": "in_progress",
                "priority": "high",
            }
        }
    )


class TaskRead(TaskBase):
    """Schema for task response details."""
    id: int = Field(..., description="Unique task identifier", examples=[1])
    owner_id: int = Field(..., description="ID of the user who owns this task", examples=[1])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Build REST API",
                "description": "Implement authentication and CRUD endpoints",
                "status": "todo",
                "priority": "high",
                "due_date": "2026-12-31T23:59:59Z",
                "owner_id": 1,
                "created_at": "2026-01-01T10:00:00Z",
                "updated_at": "2026-01-01T10:00:00Z",
            }
        },
    )


class TaskPagination(BaseModel):
    """Paginated task response envelope."""
    items: list[TaskRead] = Field(..., description="List of tasks on current page")
    total: int = Field(..., description="Total number of tasks matching criteria", examples=[42])
    skip: int = Field(..., description="Number of items skipped (offset)", examples=[0])
    limit: int = Field(..., description="Maximum items returned per page", examples=[20])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Build REST API",
                        "description": "Implement authentication and CRUD endpoints",
                        "status": "todo",
                        "priority": "high",
                        "due_date": "2026-12-31T23:59:59Z",
                        "owner_id": 1,
                        "created_at": "2026-01-01T10:00:00Z",
                        "updated_at": "2026-01-01T10:00:00Z",
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 20,
            }
        }
    )
