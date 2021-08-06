from enum import Enum

from sodalite.util import pubsub


class Mode(Enum):
    NAVIGATE = 1
    ASSIGN_CHOOSE_ENTRY = 2
    ASSIGN_CHOOSE_KEY = 3
    OPERATE = 4


class GlobalMode:

    def __init__(self):
        super().__init__()
        self.mode = Mode.NAVIGATE

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode: Mode):
        self._mode = mode
        pubsub.mode_send(self._mode)

    def __eq__(self, other):
        return self._mode == other or super.__eq__(self, other)


global_mode = GlobalMode()
