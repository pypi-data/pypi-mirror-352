import typer

from sankalp.models import Task, Focus, TaskSession, Reminder
from sankalp.db_connecter import db
from sankalp.cli_controllers import (
    task_controller,
    focus_controller,
    task_session_controller,
    reminder_controller,
)
import logging

logging.basicConfig(level=logging.INFO)

db.connect()
db.create_tables(
    [Task, Focus, TaskSession, Reminder]
)  # Initialize the database tables if not already created

app = typer.Typer()
app.add_typer(task_controller.app, name="tasks")

app.add_typer(focus_controller.app, name="focus")

app.add_typer(task_session_controller.app, name="task_sessions")
app.add_typer(task_session_controller.app, name="ts")

app.add_typer(reminder_controller.app, name="reminders")


if __name__ == "__main__":
    app()

db.close()
