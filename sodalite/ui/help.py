from functools import reduce
from typing import Optional

import urwid
from urwid import CompositeCanvas

from sodalite.ui import theme
from sodalite.ui.action import Action
from sodalite.ui.control import Control


class HelpPopup(urwid.WidgetWrap):
    signals = ['close']
    padding_y = 1
    padding_x = 3
    column_spacing = 28

    def __init__(self, control: Control):
        self.control = control
        contents = [self.createActionEntry(action) for action in self.control.action_map.values()]
        heading_text = '{:<{}}keybinding'.format('action', self.column_spacing)
        heading = urwid.Text([(theme.bold, heading_text)], wrap='clip')
        contents = [heading] + contents
        self.content_height = len(contents) + 2 * self.padding_y
        self.content_width = reduce(lambda x, y: max(x, y),
                                    map(lambda x: len(x.text), contents)) + 3 + 2 * self.padding_x
        pile = urwid.Pile(contents)
        padded = urwid.Padding(urwid.Filler(pile), align='center', left=self.padding_x, right=self.padding_x)
        box = urwid.Pile([urwid.LineBox(padded, 'help')])
        super().__init__(box)

        def keypress(*params):
            self._emit("close")

        box.keypress = keypress

    def createActionEntry(self, action: Action) -> urwid.Widget:
        key = action.keybinding
        if key == ' ':
            key = "<space>"
        elif key == 'backspace':
            key = "ctrl h"
        text = f"{action.name:<{self.column_spacing}}{key}"
        return urwid.Text(text, wrap='clip')


class HelpLauncher(urwid.PopUpLauncher):
    def __init__(self, original_widget: urwid.Widget):
        super().__init__(original_widget)
        self.control: Optional[Control] = None
        self.pop_up: Optional[HelpPopup] = None

    def open_pop_up(self, control: Control) -> None:
        self.control = control
        super().open_pop_up()

    def create_pop_up(self) -> HelpPopup:
        if self.control is None:
            raise ValueError()
        self.pop_up = HelpPopup(self.control)
        urwid.connect_signal(self.pop_up, 'close',
                             lambda button: self.close_pop_up())
        return self.pop_up

    def render(self, size, focus=False) -> CompositeCanvas:
        (self.screen_width, self.screen_height) = size
        return super().render(size, focus=focus)

    def get_pop_up_parameters(self):
        return {
            'left': self.screen_width / 2 - self.pop_up.content_width / 2,
            'top': self.screen_height / 2 - self.pop_up.content_height / 2,
            'overlay_width': self.pop_up.content_width,
            'overlay_height': self.pop_up.content_height
        }
