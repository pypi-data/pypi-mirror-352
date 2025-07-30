import datetime
from typing import Optional

from sankalp.models import Focus, Task
import logging

logger = logging.getLogger(__name__)


def create(description: Optional[str] = None):
    """
    Create a new focus session with the given description.
    """
    active_focus = Focus.get_active_focus_session()
    if active_focus:
        logger.warning(
            f"There is already an active focus session {active_focus.id}. Please close it before starting a new one."
        )
        return None
    focus = Focus.create(description=description)
    return focus


def update(focus_id: int, description: Optional[str] = None):
    """
    Update an existing focus session with the given description and tasks.
    """
    focus = Focus.get(Focus.id == focus_id)
    if description:
        focus.description = description
    focus.save()
    return focus


def close():
    """
    Close the current focus session.
    """
    focus = Focus.get_active_focus_session()
    if not focus:
        raise ValueError("No active focus session to close.")
    focus.end_time = datetime.datetime.now()
    focus.save()
    return focus


def list_all(
    started_from: datetime.datetime, started_to: datetime.datetime
) -> list[Focus]:
    """
    List all focus sessions, optionally filtered by start and end dates.
    """
    query = (
        Focus.select()
        .where((Focus.start_time >= started_from) & (Focus.start_time <= started_to))
        .order_by(Focus.start_time.desc())
    )

    focus_sessions = list(query)
    if not focus_sessions:
        logger.info("No focus sessions found.")

    return focus_sessions
