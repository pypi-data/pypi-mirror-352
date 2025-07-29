from typing import Optional
import typer
from sankalp.services import task_session_service
from rich.console import Console
from rich.table import Table

app = typer.Typer()


@app.command()
def create(task_id: int, duration: Optional[float] = 0.0):
    """
    Create a new task session with the given task ID.
    """
    try:
        task_session = task_session_service.create(task_id=task_id, duration=duration)
        typer.echo(
            f"Task session registered: {typer.style(task_session.id,bold=True)} for task {typer.style(task_id,bold=True)}"
        )
    except ValueError as e:
        typer.echo(f"Error creating task session: {e}")


def delete(task_session_id: int):
    """
    Delete a task session with the given ID.
    """
    try:
        task_session_service.delete(task_session_id)
        typer.echo(
            f"Task session {typer.style(task_session_id,bold=True)} deleted successfully."
        )
    except ValueError as e:
        typer.echo(f"Error deleting task session: {e}")


@app.command(name="list")
def list_all(focus_id: Optional[int] = None):
    """
    List all task sessions, optionally filtered by focus ID.
    """
    console = Console()
    try:
        task_sessions = task_session_service.list_all(focus_id=focus_id)
        if not task_sessions:
            typer.echo("No task sessions found.")
            return
        table = Table(
            "Id",
            "Task ID",
            "Task name",
            "Focus ID",
            "Duration (hrs)",
            "Created At",
        )
        for session in task_sessions:
            table.add_row(
                str(session.id),
                str(session.task),
                session.task.title if session.task else "N/A",
                str(session.focus),
                f"{session.duration:.2f}",
                session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        console.print(table)
    except ValueError as e:
        typer.echo(f"Error listing task sessions: {e}")
