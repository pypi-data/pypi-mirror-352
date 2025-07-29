import datetime
from typing import Optional
import typer
from sankalp.utils.table_utils import render_table
from sankalp.services import focus_service

app = typer.Typer()


@app.command()
def start(description: Optional[str] = ""):
    """
    Start a new focus session with an optional description.
    """
    focus = focus_service.create(description=description)
    if focus:
        typer.echo(f"Focus session started: {focus.id} {description}")
    else:
        typer.echo(
            "Failed to start focus session. There is already an active focus session."
        )


@app.command()
def close():
    """
    Close the current focus session.
    """
    try:
        focus = focus_service.close()
        duration = round(
            (focus.end_time - focus.start_time).total_seconds() / (60 * 60), 2
        )
        typer.echo(
            f"Focus session {typer.style(focus.id,bold=True)} of duration {typer.style(duration,bold=True)} hour closed successfully."
        )
    except Exception as e:
        typer.echo(f"Failed to close focus session: {e}")


@app.command(name="list")
def list_all(
    started_from: Optional[str] = typer.Argument(
        None, help="Filter by start date (YYYY-MM-DD HH:MM:SS)"
    ),
    started_to: Optional[str] = typer.Argument(
        None, help="Filter by end date (YYYY-MM-DD HH:MM:SS)"
    ),
):
    """
    List all focus sessions, optionally filtered by start and end dates.
    """
    started_from_dt: datetime.datetime = (
        datetime.datetime.strptime(started_from, "%Y-%m-%d %H:%M:%S")
        if started_from
        else datetime.datetime.now().replace(hour=0, minute=0, second=0)
    )
    started_to_dt: datetime.datetime = (
        datetime.datetime.strptime(started_to, "%Y-%m-%d %H:%M:%S")
        if started_to
        else datetime.datetime.now()
    )

    focus_sessions = focus_service.list_all(
        started_from=started_from_dt, started_to=started_to_dt
    )
    if not focus_sessions:
        typer.echo("No focus sessions found.")
        return
    focus_sessions_data: list = list()
    for focus in focus_sessions:
        duration = round(
            (
                (focus.end_time if focus.end_time else datetime.datetime.now())
                - focus.start_time
            ).total_seconds()
            / (60 * 60),
            2,
        )
        focus_sessions_data.append(
            [
                str(focus.id),
                focus.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                (
                    focus.end_time.strftime("%Y-%m-%d %H:%M:%S")
                    if focus.end_time
                    else "In Progress"
                ),
                str(duration),
                focus.description,
            ]
        )

        render_table(
            focus_sessions_data,
            headers=["Id", "Start Time", "End Time", "Duration (hours)", "Description"],
            title="Focus Sessions",
        )
