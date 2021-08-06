from typing import Callable

import sodalite.ui.mmode
from sodalite.core import config, action_def
from sodalite.core.action_def import ActionName
from sodalite.ui.mmode import Mode


class Action:

    def __init__(self, name: ActionName, action: Callable[[], None], modes: list[Mode] = None) -> None:
        self.name = name
        self.is_global = not modes
        self.modes = modes or []
        self.action = action
        self.keybinding = config.get().keymap.setdefault(name, action_def.default_keybindings[name])

    def handle(self, key: str) -> bool:
        if key == self.keybinding:
            if self.is_global or sodalite.ui.mmode.global_mode in self.modes:
                self.action()
                return True
        return False

    def __str__(self) -> str:
        return self.name.value


class MultiAction(Action):

    def __init__(self, name: ActionName, action: Callable[[], None], modes: list[Mode] = None) -> None:
        super().__init__(name, action, modes=modes)
