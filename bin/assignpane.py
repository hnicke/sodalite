import npyscreen
import entrypane
import theme

class AssignPane(theme.LinePrinter,entrypane.EntryPane,npyscreen.MultiLineAction):


    def __init__(self, *args, **keywords):
        npyscreen.MultiLineAction.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.handlers = {}

    def h_cursor_line_up(self, input):
        npyscreen.MultiLineAction.h_cursor_line_up(self, input)
        self.display()

    def h_cursor_line_down(self, input):
        npyscreen.MultiLineAction.h_cursor_line_down(self, input)
        self.display()
