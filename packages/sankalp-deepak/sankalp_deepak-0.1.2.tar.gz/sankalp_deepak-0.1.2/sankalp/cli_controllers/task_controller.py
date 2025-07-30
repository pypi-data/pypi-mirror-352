from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text
from sankalp.services import tasks_service
from sankalp.models import Task, Priority, Status
from sankalp.utils import color_utils

app = typer.Typer()


@app.command()
def create(
    name: str,
    priority: Optional[str] = Priority.MEDIUM.name,
    status: Optional[str] = Status.PENDING.name,
    due_date: Optional[str] = None,
    description: Optional[str] = "",
    required_time: Optional[int] = 1,
):
    """
    Create a new task with the given name, description, priority, status and due_date.
    """
    task = tasks_service.create(
        name, priority, status, due_date, description, required_time
    )
    typer.echo(
        f"Task created: {task.id} {name}, {description}, {priority}, {status} {due_date}"
    )


@app.command()
def update(
    id: int,
    name: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    description: Optional[str] = "",
    required_time: Optional[float] = None,
    allocated_time: Optional[float] = None,
):
    """
    Update an existing task with the given name, description, priority, status and due_date.
    """
    try:
        task = tasks_service.update(
            id,
            name,
            priority,
            status,
            due_date,
            description,
            required_time,
            allocated_time,
        )
        typer.echo(
            f"Task updated: {task.title}, {task.description}, {task.priority}, {task.status} {task.due_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except Exception as e:
        typer.echo(f"Failed to update Task with ID {id} due to {e}.")


@app.command(name="list")
def list_all(
    show_inactive: bool = typer.Option(
        False, "--show-inactive", "-i", help="Show inactive tasks"
    )
):
    """
    List all tasks, optionally showing inactive tasks.
    """
    console = Console()
    tasks: list[Task] = tasks_service.list_all(show_inactive)
    table = Table(
        "Id",
        "Title",
        "Description",
        "Priority",
        "Status",
        "Due date",
        "Required time (hrs)",
        "Allocated time (hrs)",
    )
    task: Task
    for task in tasks:
        priority = Priority(task.priority)
        status = Status(task.status)
        table.add_row(
            str(task.id),
            task.title,
            task.description,
            Text(priority.name, priority.color),
            Text(status.name, status.color),
            Text(task.due_at.strftime("%Y-%m-%d %H:%M:%S"), color_utils.get_due_date_color(task.due_at, task.required_time, status)),  # type: ignore
            str(round(task.required_time, 2)),
            str(round(task.allocated_time, 2)),
        )
    console.print(table)


@app.command()
def delete(id: int):
    """
    Delete a task by its ID.
    """
    try:
        task = Task.get(Task.id == id)
        task.delete_instance()
        typer.echo(f"Task with ID {id} deleted.")
    except Exception as e:
        typer.echo(f"Failed to delete Task with ID {id} due to {e}.")


if __name__ == "__main__":
    app()
