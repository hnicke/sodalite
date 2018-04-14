import curses
import logging

import npyscreen

from ui.entryview import EntryLine

logger = logging.getLogger(__name__)

COLOR_FILE = 'FILE'
COLOR_DIR = 'DIR'
COLOR_EXECUTABLE = 'EXECUTABLE'
COLOR_UNUSED = 'UNUSED'
COLOR_SYMLINK = 'SYMLINK'
COLOR_FORBIDDEN = 'FORBIDDEN'


class Theme(npyscreen.Themes.TransparentThemeLightText):

    def __init__(self, *args, **keywords):
        self.init_custom_colors()
        super().__init__(*args, **keywords)

    def init_custom_colors(self):
        for i in range(curses.COLORS):
            Theme._colors_to_define += ((str(i), i, -1),)

        Theme.default_colors['LABEL'] = '-1'
        Theme.default_colors['FILE'] = '15'
        Theme.default_colors['DIR'] = '12'
        Theme.default_colors['EXECUTABLE'] = '10'
        Theme.default_colors['SYMLINK'] = '14'
        Theme.default_colors['FORBIDDEN'] = '9'
        Theme.default_colors['UNUSED'] = '102'

    def findPair(self, caller, request='DEFAULT'):
        # gets called internally in npyscreen. Added support for dim attribute
        color = super().findPair(caller, request='DEFAULT')
        if isinstance(caller, EntryLine):
            if caller.dim:
                color = color | curses.A_DIM
        return color
