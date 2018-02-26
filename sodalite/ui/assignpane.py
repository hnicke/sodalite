import npyscreen

from core import key
from core.key import Key
from ui import entrypane, theme


class AssignState:
    CHOOSE_ENTRY = 1
    CHOOSE_KEY = 2


class AssignPane(theme.LinePrinter, entrypane.EntryPane, npyscreen.MultiLineAction):

    def __init__(self, *args, **keywords):
        npyscreen.MultiLineAction.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.navigator = self.parent.navigator
        self.data = self.parent.data
        # valid values: 'choose-entry' and 'choose-key'

        self.state = AssignState.CHOOSE_ENTRY
        self.entry_for_assignment = None
        self.handlers = {}

    def t_input_is_assign_key(self, input):
        try:
            char = chr(input)
            if not self.data.in_assign_mode:
                return False
            is_assign_key = char in key.get_all_keys()
            return is_assign_key
        except ValueError:
            return False

    def h_assign_key(self, input):
        char = chr(input)
        if self.state == AssignState.CHOOSE_ENTRY:
            match = self.parent.data.current_entry.get_child_for_key(Key(char))
            if match is not None:
                self.cursor_line = self.values.index(match)
                self.display()
                self.choose_entry(match)
        elif self.state == AssignState.CHOOSE_KEY:
            char = chr(input)
            self.navigator.assign_key(Key(char), self.entry_for_assignment.path)
            self.state = AssignState.CHOOSE_ENTRY
            self.cursor_line = 0
            self.parent.controller.h_toggle_assign_mode("_")
        return

    def h_choose_selection(self, input):
        entry = self.values[self.cursor_line]
        self.choose_entry(entry)

    def choose_entry(self, entry):
        if self.state == AssignState.CHOOSE_ENTRY:
            self.entry_for_assignment = entry
            self.state = AssignState.CHOOSE_KEY
            self.parent.redraw_statusbar()

    def h_cursor_line_up(self, input):
        if self.state == AssignState.CHOOSE_ENTRY:
            npyscreen.MultiLineAction.h_cursor_line_up(self, input)
            self.display()

    def h_cursor_line_down(self, input):
        if self.state == AssignState.CHOOSE_ENTRY:
            npyscreen.MultiLineAction.h_cursor_line_down(self, input)
            self.display()

    def when_parent_changes_value(self):
        self.values = self.parent.value
