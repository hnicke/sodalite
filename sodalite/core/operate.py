import os
import time
from typing import Dict

from sodalite.core.entry import Entry


def rename(entry: Entry, new_name: str):
    os.rename(entry.path, os.path.join(entry.dir, new_name))
    entry.name = new_name
    # dao.rename_entry(entry, new_name)


class Operation:
    def __init__(self, action_name, params: Dict[str, str] = None, timestamp=None):
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
