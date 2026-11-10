from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.task import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    update_task,
)
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskPagination, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Create a new task owned by the currently authenticated user.",
    responses={
        201: {"description": "Task created successfully", "model": TaskRead},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def create_new_task(
    task_in: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    """Create a new task for the current user."""
    task = create_task(db=db, task_in=task_in, owner_id=current_user.id)
    return TaskRead.model_validate(task)


@router.get(
    "",
    response_model=TaskPagination,
    summary="List tasks",
    description="Retrieve paginated tasks for the authenticated user with optional filtering, search, and sorting.",
    responses={
        200: {"description": "Paginated list of tasks", "model": TaskPagination},
        401: {"description": "Unauthorized"},
    },
)
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status: TaskStatus | None = Query(
        default=None,
        description="Filter tasks by status (todo, in_progress, done)",
    ),
    priority: TaskPriority | None = Query(
        default=None,
        description="Filter tasks by priority (low, medium, high)",
    ),
    search: str | None = Query(
        default=None,
        description="Search term matching task title",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip (offset)",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return (1-100)",
    ),
    sort_by: Literal["created_at", "due_date", "priority"] = Query(
        default="created_at",
        description="Field to sort tasks by",
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
        description="Sort direction (asc or desc)",
    ),
) -> TaskPagination:
    """List tasks owned by the current authenticated user."""
    items, total = get_tasks(
        db=db,
        owner_id=current_user.id,
        status=status,
        priority=priority,
        search=search,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )
    return TaskPagination(
        items=[TaskRead.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{id}",
    response_model=TaskRead,
    summary="Get task by ID",
    description="Retrieve a specific task by its ID. Only tasks owned by the current user can be accessed.",
    responses={
        200: {"description": "Task details", "model": TaskRead},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
)
def get_task(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    """Retrieve an existing task by ID for the current user."""
    task = get_task_by_id(db=db, task_id=id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskRead.model_validate(task)


@router.patch(
    "/{id}",
    response_model=TaskRead,
    summary="Update task partially",
    description="Partially update a task by its ID. Only tasks owned by the current user can be updated.",
    responses={
        200: {"description": "Updated task", "model": TaskRead},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
def patch_task(
    id: int,
    task_in: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    """Partially update an existing task for the current user."""
    task = get_task_by_id(db=db, task_id=id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    updated = update_task(db=db, task=task, task_in=task_in)
    return TaskRead.model_validate(updated)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task by its ID. Only tasks owned by the current user can be deleted.",
    responses={
        204: {"description": "Task successfully deleted"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
)
def remove_task(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Delete an existing task for the current user."""
    task = get_task_by_id(db=db, task_id=id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    delete_task(db=db, task=task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
