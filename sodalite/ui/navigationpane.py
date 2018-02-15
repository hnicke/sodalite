import npyscreen

from ui import entrypane, theme


class NavigationPane(theme.LinePrinter, entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.handlers = {
        }
        return

    def t_input_is_navigation_key(self, input):
        try:
            if self.parent.in_assign_mode:
                return False
            char = chr(input)
            is_navigation_key = char == "." or char in [entry.key.value for entry in self.values]
            return is_navigation_key
        except ValueError:
            return False

    def when_parent_changes_value(self):
        self.values = self.parent.value
