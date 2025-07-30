from typing import Optional

from sankalp.models import TaskSession, Task, Focus
from sankalp.services import focus_service


def create(task_id: int, duration: Optional[float] = 0.0) -> TaskSession:
    """
    Create a new task session with the given task ID, focus ID, and duration.
    """
    focus = Focus.get_active_focus_session()
    if not focus:
        raise ValueError(
            "No active focus session found. Please start a focus session before creating a task session."
        )
    task = Task.get(Task.id == task_id)
    if not task:
        raise ValueError(f"Task with ID {task_id} does not exist.")
    task.allocated_time = task.allocated_time + duration
    task_session = TaskSession.create(
        task_id=task_id, focus_id=focus.id, duration=duration
    )
    task.save()
    return task_session


def delete(task_session_id: int):
    """
    Delete a task session with the given ID.
    """
    try:
        task_session = TaskSession.get(TaskSession.id == task_session_id)
        task = task_session.task
        task.allocated_time -= task_session.duration
        task.save()
        task_session.delete_instance()
    except Exception as e:
        raise ValueError(
            f"Failed to delete task session with ID {task_session_id}: {e}"
        ) from e


def list_all(focus_id: Optional[int] = None) -> list[TaskSession]:
    """
    List all task sessions, optionally filtered by focus ID.
    """
    focus = None
    if not focus_id:
        focus = Focus.get_active_focus_session()
        if not focus:
            raise ValueError(
                "No active focus session found. Please start a focus session to list task sessions or pass focus id."
            )
    else:
        focus = Focus.get(Focus.id == focus_id)
        if not focus:
            raise ValueError(f"Focus with ID {focus_id} does not exist.")
    return list(
        TaskSession.select()
        .where(TaskSession.focus == focus)
        .order_by(TaskSession.created_at.desc())
    )
