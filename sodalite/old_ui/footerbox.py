import curses
import logging
from typing import List

import npyscreen

from core.hook import Hook
from old_ui.viewmodel import ViewModel

logger = logging.getLogger(__name__)


class FooterBox(npyscreen.BoxBasic):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, height=3, *args, **keywords)
        self.padding = 4
        self.handlers = {}

    def resize(self):
        self.rely = self.parent.lines - self.height
        super().resize()


class NotifyBox(FooterBox):

    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.message = ""
        self.attributes = []

    def notify(self, message: str, attr=curses.A_NORMAL):
        self.message = message
        self.attributes = [attr] * len(message)

    def update(self, clear=True):
        super().update(clear)
        if not self.hidden:
            center = (self.width - len(self.message)) // 2
            self.add_line(self.rely + 1, center, self.message, self.attributes, self.width - 2)


class HookBox(FooterBox):

    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.values: List[Hook] = []
        self._data: ViewModel = None

    def data(self, data: ViewModel):
        if self._data is not None:
            self._data.unregister(self)
        self._data = data
        self._data.register(self)

    data = property(None, data)

    def on_update(self):
        self.values = [hook for hook in self._data.current_entry.hooks if hook.label is not None]
        pass

    def update(self, clear=True):
        super().update(clear)
        if self.hidden:
            self.clear()
            return
        self.resize()

        hooks = [get_hook_representation(hook) for hook in self.values]
        representations = [hook[0] for hook in hooks]
        column_width = self.compute_column_width(representations)

        start_x = self.relx + 2
        start_y = self.rely + 1
        x = start_x
        y = start_y
        max_x = self.relx + self.width
        max_y = self.rely + self.height - 2
        for hook in hooks:
            if y > max_y:
                self.height += 1
                self.rely -= 1
                self.parent.DISPLAY()
                break
            self.add_line(y, x, hook[0], hook[1], self.width - 2)
            x += column_width
            if x + column_width - self.padding > max_x:
                x = start_x
                y += 1

    def compute_column_width(self, hooks: List[str]):
        max_size = 0
        for hook in hooks:
            if len(hook) > max_size:
                max_size = len(hook)
        column_width = max_size + self.padding
        return column_width


def get_hook_representation(hook: Hook) -> (str, List[int]):
    spacing = 4
    representation = f"{hook.key:<{spacing}}{hook.label}"
    attributes = [curses.A_UNDERLINE] * len(hook.key)
    attributes.extend([curses.A_NORMAL] * (spacing - len(hook.key) + len(hook.label)))
    return representation, attributes
