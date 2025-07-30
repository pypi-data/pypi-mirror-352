import datetime

from sankalp.models import Status


def get_due_date_color(
    due_date: datetime.datetime, required_time: float, status: Status
) -> str:
    """
    Get the color for the due date based on how far in the future it is.
    """
    if not status.is_active():
        return ""

    now = datetime.datetime.now()
    delta = due_date - now
    if delta.total_seconds() < 0:
        return "red"
    elif (
        delta.total_seconds() < required_time * 60 * 60
    ):  # less than required time in seconds
        return "yellow"
    else:
        return ""
