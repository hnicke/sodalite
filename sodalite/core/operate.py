import time

from sodalite.core.entry import Entry


def rename(entry: Entry, new_name: str):
    entry.path.rename(entry.dir / new_name)
    entry.name = new_name


class Operation:
    def __init__(self, action_name, params: dict[str, str] = None, timestamp=None):
        self.action_name = action_name
        if not params:
            params = {}
        self.params = params
        if not timestamp:
            timestamp = int(time.time() * 1000)
        self.timestamp = timestamp

    def do(self):
        pass

    def undo(self):
        pass
