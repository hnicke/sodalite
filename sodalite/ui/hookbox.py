import urwid

from sodalite.core.entry import Entry
from sodalite.core.hook import Hook
from sodalite.ui import graphics
from sodalite.util import pubsub


class HookBox(urwid.WidgetWrap):
    def __init__(self, parent: urwid.Frame):
        self.padding = 4
        self.parent = parent
        grid = urwid.GridFlow([], 1, self.padding, 0, 'left')
        padded_grid = urwid.Padding(grid, left=1)
        box = urwid.LineBox(padded_grid, tline='')
        super().__init__(box)
        pubsub.entry_connect(self.on_navigated)

    def on_navigated(self, entry: Entry):
        with graphics.DRAW_LOCK:
            self._w.base_widget.contents = [(HookCell(hook), self._w.base_widget.options()) for hook in
                                            entry.hooks if hook.label]
            if len(self._w.base_widget.contents) > 0:
                self.update_cell_width()
                self.parent.footer = self
            else:
                self.parent.footer = None

    def update_cell_width(self):
        max_width = 0
        for width in [cell.width for cell, option in self._w.base_widget.contents]:
            max_width = max(max_width, width)
        self._w.base_widget.cell_width = max_width


class HookCell(urwid.WidgetWrap):
    def __init__(self, hook: Hook):
        markup, plain = get_hook_representation(hook)
        cell = urwid.Text(markup)
        self.width = len(plain)
        super().__init__(cell)


def get_hook_representation(hook: Hook):
    spacing = 4
    plain = f"{hook.key:<{spacing}}{hook.label}"
    markup = [('bold', f"{hook.key:<{spacing}}"), f"{hook.label}"]
    # TODO add attributes
    # attributes = [curses.A_UNDERLINE] * len(hook.key)
    # attributes.extend([curses.A_NORMAL] * (spacing - len(hook.key) + len(hook.label)))
    return markup, plain
