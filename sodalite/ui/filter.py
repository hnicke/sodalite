import curses
import logging

import npyscreen

logger = logging.getLogger(__name__)


class Filter(npyscreen.Textfield):

    def __init__(self, screen, data, *args, **keywords):
        super(Filter, self).__init__(screen, *args, **keywords)
        self.data = data
        self.search_mode = False
        self.add_handlers({
            curses.ascii.ESC: self.__reset,
            curses.KEY_BACKSPACE: self.h_delete_left,
        })
        self.editable = False

    def t_filter(self, input):
        try:
            char = chr(input)
            return char == '/'
        except (ValueError, TypeError):
            return False

    def when_value_edited(self):
        self.data.filter(self.value[1:])
        # somehow hookpane is glitching: update 'solves' this
        self.parent.hookpane.update()

    def trigger(self, input):
        self.editable = True
        self.value = "/"
        self.edit()

    def __reset(self, _):
        self.clear_search()

    # clears the search and also any applied filter on data
    def clear_search(self, *args):
        self.important = False
        self.editing = False
        self.editable = False
        self.value = ""
        self.data.filter("")

    def h_delete_left(self, ch):
        if len(self.value) != 1:
            super().h_delete_left(ch)
