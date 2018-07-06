import time
from typing import Dict


class Operation:
    def __init__(self, action_name, params: Dict[str, str] = None, timestamp=None):
        self.action_name = action_name
        if not params:
            params = {}
        self.params = params
        if not timestamp:
            timestamp = int(time.time() * 1000)
        self.timestamp = timestamp
