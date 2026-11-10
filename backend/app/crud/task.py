from typing import Literal
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
    """Create a new task owned by the specified user."""
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        owner_id=owner_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: int, owner_id: int) -> Task | None:
    """Retrieve a single task strictly filtered by task ID and owner ID."""
    stmt = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    return db.scalars(stmt).first()


def get_tasks(
    db: Session,
    owner_id: int,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: Literal["created_at", "due_date", "priority"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> tuple[list[Task], int]:
    """Retrieve tasks for the specified owner with filters, search, sorting, and pagination."""
    # Build filter conditions
    conditions = [Task.owner_id == owner_id]

    if status is not None:
        conditions.append(Task.status == status)

    if priority is not None:
        conditions.append(Task.priority == priority)

    if search:
        search_pattern = f"%{search.strip()}%"
        conditions.append(Task.title.ilike(search_pattern))

    # Base query for count
    count_stmt = select(func.count(Task.id)).where(*conditions)
    total = db.scalar(count_stmt) or 0

    # Base query for items
    query = select(Task).where(*conditions)

    # Determine sort attribute
    sort_col = getattr(Task, sort_by)
    if order == "desc":
        sort_expr = sort_col.desc().nullslast() if sort_by == "due_date" else sort_col.desc()
    else:
        sort_expr = sort_col.asc().nullslast() if sort_by == "due_date" else sort_col.asc()

    query = query.order_by(sort_expr).offset(skip).limit(limit)
    items = list(db.scalars(query).all())

    return items, total


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    """Update an existing task with partial fields."""
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    """Delete a task from the database."""
    db.delete(task)
    db.commit()
