import curses

import npyscreen

from core.hook import HookEngine
from core.navigator import Navigator
from ui import commandline, navigationpane, assignpane, actionpane
from ui.assignpane import AssignState
from ui.controller import Controller
from ui.viewmodel import ViewModel


class MainForm(npyscreen.FormBaseNew):

    def __init__(self, navigator: Navigator, hook_engine: HookEngine, cycle_widgets=True, *args, **keywords):
        self.hook_engine = hook_engine
        self.navigator = navigator
        self.data = ViewModel(navigator)
        self.entry_for_assignment = None
        self.navigation_mode_handlers = None
        self.assign_mode_handlers = None
        self.handlers = None
        self.complex_handlers = None
        super(MainForm, self).__init__(cycle_widgets=cycle_widgets, *args, **keywords)
        self.controller = Controller(self, self.data, navigator, hook_engine)

    def draw_form(self):
        max_y, max_x = self.lines, self.columns
        self.curses_pad.hline(0, 0, curses.ACS_HLINE, max_x - 1)
        self.curses_pad.hline(max_y - 2, 0, curses.ACS_HLINE, max_x - 1)

    def create(self):
        self.populate()
        self.data.register(self)

    def populate(self):
        MAXY, MAXX = self.lines, self.columns
        middle_x = MAXX // 2
        spacing = 1
        startline = 3
        self.statusbar = self.add(npyscreen.FixedText, relx=3 * spacing, rely=1)
        self.navigationpane = self.add(navigationpane.NavigationPane,
                                       relx=spacing,
                                       rely=startline,
                                       max_width=middle_x - (2 * spacing),
                                       )
        self.assignpane = self.add(assignpane.AssignPane,
                                   relx=spacing,
                                   rely=startline,
                                   max_width=middle_x - (2 * spacing),
                                   hidden=True,
                                   always_show_cursor=True,
                                   editable=False,
                                   )
        self.actionpane = self.add(actionpane.ActionPane,
                                   relx=middle_x + spacing,
                                   rely=startline,
                                   max_width=middle_x - (4 * spacing),
                                   data=self.data
                                   )
        self.commandline = self.add(commandline.Commandline,
                                    relx=spacing,
                                    rely=MAXY - 1,
                                    max_height=1,
                                    begin_entry_at=0,
                                    use_max_space=True,
                                    data=self.data,
                                    )

    def resize(self):
        super(MainForm, self).resize()
        MAXY, MAXX = self.lines, self.columns
        self.commandline.rely = MAXY - 1

    def redraw_statusbar(self):
        if self.data.in_assign_mode:
            if self.assignpane.state == AssignState.CHOOSE_ENTRY:
                self.set_title("assign key: choose entry")
            else:
                self.set_title("assign key: choose new key")
        else:
            self.set_title_to_cwd()

    def set_title_to_cwd(self):
        self.set_title(self.data.current_entry.realpath)

    def set_title(self, title):
        self.statusbar.value = " " + title
        self.statusbar.display()

    def update(self):
        self.set_value(self.data.filtered_children)
        self.redraw_statusbar()
        self.display()
