import npyscreen

from core import key
from core.mylogger import logger
from ui import entrypane, theme


class AssignPane(theme.LinePrinter, entrypane.EntryPane, npyscreen.MultiLineAction):

    def __init__(self, *args, **keywords):
        npyscreen.MultiLineAction.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.navigator = self.parent.navigator
        # valid values: 'choose-entry' and 'choose-key'
        self.assign_mode_progress = 'choose-entry'
        self.handlers = {}

    def t_input_is_assign_key(self, input):
        try:
            char = chr(input)
            if not self.parent.in_assign_mode:
                return False
            is_assign_key = char in key.get_all_keys() or char == "."
            return is_assign_key
        except ValueError:
            return False

    def h_assign_key(self, input):
        char = chr(input)
        if self.assign_mode_progress == 'choose-entry':
            matches = [x for x in self.values if x.key.value == char]
            if len(matches) == 1:
                entry = matches[0]
                self.cursor_line = self.values.index(entry)
                self.display()
                self.choose_entry(entry)
            elif len(matches) < 0:
                pass
            else:
                logger.error(
                    "While assigning an entry for key change, found '{}'entries for given key '{}'".format(len(matches),
                                                                                                           char))
        elif self.assign_mode_progress == 'choose-key':
            char = chr(input)
            self.navigator.assign_key(self.entry_for_assignment, char)
            self.assign_mode_progress == 'choose-entry'
            self.cursor_line = 0
            self.parent.h_toggle_assign_mode("_")
        return

    def h_choose_selection(self, input):
        entry = self.values[self.cursor_line]
        self.choose_entry(entry)

    def choose_entry(self, entry):
        if self.assign_mode_progress == 'choose-entry':
            self.entry_for_assignment = entry
            self.assign_mode_progress = 'choose-key'
            self.parent.redraw_statusbar()

    def h_cursor_line_up(self, input):
        if self.assign_mode_progress == 'choose-entry':
            npyscreen.MultiLineAction.h_cursor_line_up(self, input)
            self.display()

    def h_cursor_line_down(self, input):
        if self.assign_mode_progress == 'choose-entry':
            npyscreen.MultiLineAction.h_cursor_line_down(self, input)
            self.display()

    def when_parent_changes_value(self):
        self.values = self.parent.value
