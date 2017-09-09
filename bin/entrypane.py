import curses
import time
import key
from mylogger import logger

# baseclass which specifies common behaviour
class EntryPane:

    def __init__(self):
        self.handlers = {
                curses.ascii.SP:    self.h_scroll_page_down,
                "^B":    self.h_scroll_page_up,
                "^U":    self.h_scroll_half_page_up,
                "^D":    self.h_scroll_half_page_down,
                }
        return

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

    def input_is_navigation_key(self, input):
        char = chr(input)
        is_navigation_key = (char in key.get_all_keys() or char == '.')
        return is_navigation_key

    def display_value( self, vl ):
        return "  {}{}".format(vl.key.value.ljust(4), vl.name.ljust(30))
