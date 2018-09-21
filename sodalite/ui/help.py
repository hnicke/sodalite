import urwid

from ui.action import Action
from ui.control import Control


class HelpPopup(urwid.WidgetWrap):
    signals = ['close']

    def __init__(self, control: Control):
        available_keys = AvailableKeys(control)
        pile = urwid.Pile([available_keys])
        fill = urwid.Filler(pile)
        super().__init__(fill)

        def keypress(*params):
            self._emit("close")

        fill.keypress = keypress


class AvailableKeys(urwid.Pile):

    def __init__(self, control: Control):
        self.control = control
        self.column_spacing = 28
        contents = [self.createActionEntry(action) for action in self.control.action_map.values()]
        heading_text = '{:<{}}keybinding'.format('action', self.column_spacing)
        heading = urwid.Text([('bold', heading_text)])
        contents = [heading] + contents
        super().__init__(contents)

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
        self.control = None

    def open_pop_up(self, control: Control):
        self.control = control
        super().open_pop_up()

    def create_pop_up(self):
        pop_up = HelpPopup(self.control)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def render(self, size, focus=False):
        (self.screen_width, self.screen_height) = size
        return super().render(size, focus=focus)

    def get_pop_up_parameters(self):
        return {'left': 5, 'top': 1, 'overlay_width': self.screen_width - 6, 'overlay_height': self.screen_height - 2}
