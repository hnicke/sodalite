import npyscreen

from ui import entrypane, theme


class NavigationPane(theme.LinePrinter, entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.handlers = {
        }

    def when_parent_changes_value(self):
        self.values = self.parent.value
