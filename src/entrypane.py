import curses
import time
import key
from mylogger import logger

# baseclass which specifies common behaviour
class EntryPane:

    def __init__(self):
        self.handlers = {
                }

    def h_scroll_half_page_down(self, input):
        self.start_display_at += len(self._my_widgets) // 2
        self.cursor_line += len(self._my_widgets) // 2

    def h_scroll_half_page_up(self, input):
        self.start_display_at -= len(self._my_widgets) // 2
        self.cursor_line -= len(self._my_widgets)

    def h_scroll_page_down(self, input):
        self.start_display_at += len(self._my_widgets)
        self.cursor_line += len(self._my_widgets)

    def h_scroll_page_up(self, input):
        self.start_display_at -= len(self._my_widgets)
        self.cursor_line -= len(self._my_widgets)

    def display_value( self, vl ):
        return "  {}{}".format(vl.key.value.ljust(4), vl.name.ljust(30))
