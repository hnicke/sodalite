import time

from sodalite.core.entry import Entry


def rename(entry: Entry, new_name: str) -> None:
    entry.path.rename(entry.dir / new_name)
    entry.name = new_name


class Operation:
    def __init__(self, action_name: str, params: dict[str, str] = None, timestamp: int = None) -> None:
        self.action_name = action_name
        self.params = params or {}
        self.timestamp = timestamp or int(time.time() * 1000)

    def do(self) -> None:
        pass

    def undo(self) -> None:
        pass
