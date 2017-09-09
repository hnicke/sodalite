import npyscreen
import theme
import entrypane

class ActionPane(theme.LinePrinter, entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.core = self.parent.parentApp.core
        self.complex_handlers = [
                ]
        self.add_handlers({
            })
        return
