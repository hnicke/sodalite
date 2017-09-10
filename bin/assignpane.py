import npyscreen
import entrypane
import theme

class AssignPane(theme.LinePrinter,entrypane.EntryPane,npyscreen.MultiLineAction):


    def __init__(self, *args, **keywords):
        npyscreen.MultiLineAction.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)
