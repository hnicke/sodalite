import logging
import os
import time
from enum import Enum

import npyscreen
from npyscreen import Form
from npyscreen.wgwidget import Widget

from core.entry import Entry, EntryType
from core.navigator import Navigator
from ui import formatting, theme
from ui.control import EntryControl, MainControl, SplitControl
from ui.filter import Filter
from ui.viewmodel import ViewModel, Mode

logger = logging.getLogger(__name__)


class Position(Enum):
    LEFT = 1
    RIGHT = 2


class EntryLine(npyscreen.Textfield):

    def __init__(self, screen, **keywords):
        self.dim = False
        super().__init__(screen, **keywords)


class EntryPager(npyscreen.MultiLineEditable):
    _contained_widgets = EntryLine

    def display_value(self, entry):
        spacing = min((1 + (self.width // 25)), 3)
        spacing_left = ' ' * (spacing - 1)
        spacing_right = ' ' * spacing
        key = " " if entry.key.value == "" else entry.key.value
        return "{}{}{}{}".format(spacing_left, key, spacing_right, entry.name)

    def _print_line(self, line, value_indexer):
        """overwrites npyscreen function"""
        try:
            entry = self.values[value_indexer]
            self._set_line_values(line, value_indexer)
            self.set_format(line, entry)
            self._set_line_highlighting(line, value_indexer)
        except IndexError:
            pass

    def set_format(self, line, entry: Entry):
        if not entry.readable:
            color = theme.COLOR_FORBIDDEN
        elif entry.frequency == 0:
            color = theme.COLOR_UNUSED
            line.dim = True
        else:
            if entry.frequency < 5:
                line.dim = True
                line.show_bold = False
            elif entry.frequency < 10:
                line.dim = False
                line.show_bold = False
            else:
                line.show_bold = True

            if entry.type == EntryType.DIRECTORY:
                color = theme.COLOR_DIR
            elif entry.type == EntryType.SYMLINK:
                color = theme.COLOR_SYMLINK
            elif entry.executable:
                color = theme.COLOR_EXECUTABLE
            else:
                color = theme.COLOR_FILE
        line.color = color

    def h_scroll_page_down(self, ch):
        self.h_cursor_page_down(ch)
        self.update()

    def h_scroll_page_up(self, ch):
        self.h_cursor_page_up(ch)
        self.update()

    def h_scroll_half_page_up(self, ch):
        # copied and modified from npyscreen
        offset = (len(self._my_widgets) - 1) // 2
        self.cursor_line -= offset
        if self.cursor_line < 0:
            self.cursor_line = 0
        self.start_display_at -= offset
        if self.start_display_at < 0:
            self.start_display_at = 0
        self.update()

    def h_scroll_half_page_down(self, ch):
        # copied and modified from npyscreen
        offset = (len(self._my_widgets) - 1) // 2
        self.cursor_line += offset
        if self.cursor_line >= len(self.values) - 1:
            self.cursor_line = len(self.values) - 1
        if not (self.start_display_at + offset) > len(self.values):
            self.start_display_at += offset
            if self.start_display_at > len(self.values) - (len(self._my_widgets) - 1):
                self.start_display_at = len(self.values) - (len(self._my_widgets) - 1)
        self.update()


class EntryBox(npyscreen.MultiLineEditableBoxed):
    _contained_widget = EntryPager
    _contained_widget_arguments = {'slow_scroll': True}
    user_home = os.getenv('HOME')

    def __init__(self, screen, position: Position, splitter, main_control: MainControl, **keywords):
        self.splitter = splitter
        super().__init__(screen, editable=False, **keywords)
        self.handlers = {}
        self.multiline = self._my_widgets[0]
        self.navigator = Navigator()
        self.data = ViewModel(self.navigator)
        self.values = self.data.filtered_children
        self.position = position
        self.filter = self.parent.add(Filter,
                                      data=self.data,
                                      rely=-5,
                                      )
        info_value = f'18.4KB'
        self.info = self.parent.add(npyscreen.FixedText,
                                    rely=-5,
                                    value=info_value,
                                    editable=False
                                    )
        self.data.register(self, immediate_update=False)
        self.controller = EntryControl(self, self.navigator, self.data, main_control)

    def on_update(self):
        """
        callback: data changed
        """
        if not self.hidden:
            self.multiline.reset_cursor()
            self.set_title()
            self.set_size_label()
            self.update()

    def set_title(self):
        mode = self.data.mode
        if mode == Mode.NORMAL:
            self.set_title_to_cwd()
        elif mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.name = "assign key: choose entry"
        elif mode == Mode.ASSIGN_CHOOSE_KEY:
            self.name = "assign key: choose new key"

    def set_title_to_cwd(self):
        cwd = self.data.current_entry.path
        if cwd.startswith(EntryBox.user_home):
            cwd = "~" + cwd[len(EntryBox.user_home):]
        max_length = self.width - 9  # this is how npyscreen renders titles
        if len(cwd) > max_length:
            cutoff = len(cwd) - max_length + 2
            cwd = cwd[cutoff:]
        self.name = cwd

    def set_size_label(self):
        value = ""
        if not self.data.current_entry.is_dir():
            value = formatting.format_size(self.data.current_entry.size)
        self.info.value = value

    def visible(self, visible: bool):
        self.hidden = not visible
        self.info.hidden = not visible
        self.filter.hidden = not visible
        if not visible:
            self.data.unregister(self)
        if visible:
            self.data.register(self)

    def resize(self):
        calculate_sizes(self, self.parent, self.splitter.split)
        self.multiline.rely = self.rely + 1
        self.multiline.height = self.height - 3
        self.multiline.relx = self.relx + 2
        self.multiline.width = self.width - 3

        self.filter.relx = self.relx + 2
        self.filter.rely = self.rely + self.height - 2
        self.info.rely = self.filter.rely
        self.filter.width = self.relx + self.width - len(self.info.value) - 5
        self.info.relx = self.relx + self.width - len(self.info.value) - 2
        self.info.width = len(self.info.value)
        super().resize()
        self.multiline.resize()

    def update(self, clear=True):
        if not self.hidden:
            self.resize()  # hookpane height could have changed..
            self.set_title()
            super().update(clear)
            self.filter.update()
            self.info.update()


class EntrySplitter(Widget):

    def __init__(self, screen, main_control: MainControl, **keywords):
        self.split = False
        super().__init__(screen, **keywords)
        self.handlers = {}
        self.left_window = self.parent.add(EntryBox,
                                           position=Position.LEFT,
                                           main_control=main_control,
                                           splitter=self,
                                           rely=0,
                                           )
        self.right_window = self.parent.add(EntryBox,
                                            position=Position.RIGHT,
                                            main_control=main_control,
                                            splitter=self,
                                            rely=0,
                                            hidden=True
                                            )
        self.right_window.visible(False)
        self.left_window.controller.activate()
        SplitControl(self, main_control)


    def h_toggle_split(self, input):
        self.toggle_split()

    def toggle_split(self):
        self.split = not self.split
        self.right_window.visible(self.split)
        self.parent.display()

    def resize(self):
        self.height = get_max_height(self.parent)
        self.width = self.parent.columns


def get_split_x(screen: Form) -> int:
    return screen.columns // 2


def get_max_height(screen: Form) -> int:
    return screen.lines - screen.hookpane.height + 1


def calculate_sizes(widget, screen: Form, split: bool):
    if widget.position == Position.LEFT:
        calculate_left_size(widget, screen, split)
    else:
        calculate_right_size(widget, screen, split)


def calculate_left_size(widget: Widget, screen: Form, split: bool):
    if split:
        width = get_split_x(screen)
    else:
        width = screen.columns - 1
    height = get_max_height(screen)
    widget.relx = 0
    widget.rely = 0
    widget.width = width
    widget.height = height


def calculate_right_size(widget: Widget, screen: Form, split: bool):
    if split:
        width = screen.columns - get_split_x(screen)
        height = get_max_height(screen)
        widget.relx = get_split_x(screen) - 1
        widget.rely = 0
        widget.width = width
        widget.height = height
