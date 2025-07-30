import datetime
from typing import Optional

from sankalp.models import Priority, Status, Task
from sankalp.services import reminder_service


def create(
    name: str,
    priority: Optional[str] = Priority.MEDIUM.name,
    status: Optional[str] = Status.PENDING.name,
    due_date: Optional[str] = None,
    description: Optional[str] = None,
    required_time: Optional[int] = 1,
) -> Task:
    """
    Create a new task with the given name, description, priority, status and due_date.
    """
    task = Task.create(
        title=name,
        description=description,
        priority=Priority[priority].value if priority else None,
        status=Status[status].value if status else None,
        due_at=(
            datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            if due_date
            else None
        ),
        required_time=required_time,
    )
    reminder_service.create_reminders_from_policy(task)
    return task


def update(
    id: int,
    name: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    description: Optional[str] = None,
    required_time: Optional[float] = None,
    allocated_time: Optional[float] = None,
) -> Task:
    task = Task.get(Task.id == id)
    if name:
        task.title = name
    if description:
        task.description = description
    if priority:
        task.priority = Priority[priority].value
    if status:
        task.status = Status[status].value
    if due_date:
        task.due_at = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
    if required_time is not None:
        task.required_time = required_time
    if allocated_time is not None:
        task.allocated_time = allocated_time
    task.save()
    return task


def list_all(return_inactive: bool = False) -> list[Task]:
    """
    List all tasks, optionally including inactive ones.
    """
    if return_inactive:
        return list(Task.select().order_by(Task.due_at))
    else:
        return list(
            Task.select()
            .where(Task.status << Status.get_active_status())
            .order_by(Task.due_at)
        )
