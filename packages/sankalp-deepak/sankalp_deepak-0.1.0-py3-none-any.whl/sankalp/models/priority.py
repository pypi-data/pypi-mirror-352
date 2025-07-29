from enum import Enum


class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    NONE = 4

    @property
    def color(self) -> str:
        return _PRIORITY_COLOR_MAP.get(self, "black")


_PRIORITY_COLOR_MAP = {
    Priority.CRITICAL: "red",
    Priority.HIGH: "orange3",
    Priority.MEDIUM: "yellow",
    Priority.LOW: "bright_cyan",
    Priority.NONE: "grey0",
}
