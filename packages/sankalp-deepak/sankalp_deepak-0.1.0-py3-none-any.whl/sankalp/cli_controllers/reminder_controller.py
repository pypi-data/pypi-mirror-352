from typing import Optional
import typer
from sankalp.utils.table_utils import render_table
from sankalp.services import reminder_service
import datetime

app = typer.Typer()


@app.command()
def create(task_id: int, remind_at: str):
    """
    Create a new reminder for a task.
    """
    try:
        remind_at_dt = datetime.datetime.strptime(remind_at, "%Y-%m-%d %H:%M:%S")
        reminder = reminder_service.create(task_id, remind_at_dt)
        typer.echo(f"Reminder created with ID: {reminder.id}")
    except ValueError as e:
        typer.echo(f"Error parsing date: {e}")


@app.command()
def delete(reminder_id: int):
    """
    Delete a reminder by its ID.
    """
    try:
        reminder_service.delete(reminder_id)
        typer.echo(f"Reminder with ID {reminder_id} deleted successfully.")
    except Exception as e:
        typer.echo(f"Error deleting reminder: {e}")


@app.command("list")
def list_all(
    task_id: Optional[int] = None,
    show_inactive: bool = False,
):
    """
    List all reminders for a specific task or all active reminders.
    """
    if task_id is not None:
        reminders = reminder_service.get_reminders_for_task(task_id)
    elif not show_inactive:
        reminders = reminder_service.get_active_reminders()
    else:
        reminders = reminder_service.get_all_reminders()
    headers = ["ID", "Task ID", "Task Name", "Remind At", "Is Active"]
    data: list = []
    for reminder in reminders:
        data.append(
            [
                str(reminder.id),
                str(reminder.task.id),
                reminder.task.title,
                reminder.remind_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Active" if reminder.is_active else "Inactive",
            ]
        )
    render_table(
        title="Reminders",
        headers=headers,
        data=data,
    )
