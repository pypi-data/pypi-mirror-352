from enum import Enum


class Status(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4

    @property
    def color(self) -> str:
        return _STATUS_COLOR_MAP.get(self, "black")

    @classmethod
    def get_active_status(cls) -> list[int]:
        return [cls.PENDING.value, cls.IN_PROGRESS.value]

    def is_active(self) -> bool:
        return self.value in self.get_active_status()


_STATUS_COLOR_MAP = {
    Status.PENDING: "yellow",
    Status.IN_PROGRESS: "bright_cyan",
    Status.COMPLETED: "green",
    Status.FAILED: "red",
    Status.CANCELLED: "grey0",
}
