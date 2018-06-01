import logging

import pyperclip
import urwid
from urwid import AttrSpec

from ui import theme, app
from ui.entrylist import EntryList
from ui.filepreview import FilePreview
from ui.filter import Filter
from ui.viewmodel import ViewModel, Mode
from util import environment

logger = logging.getLogger(__name__)


class MainPane(urwid.WidgetWrap):

    def __init__(self, model: ViewModel):
        self.model = model
        self.navigator = self.model.navigator
        self.entry_list = EntryList(self, self.model, self.navigator)
        self.file_preview = FilePreview(model)
        self.body = self.entry_list
        self.frame = urwid.Frame(self.body)
        self.box = urwid.LineBox(self.frame, title_align='left')
        self.box.title_widget.set_layout('right', 'clip')
        self.model.register(self)

        super().__init__(self.box)

    def on_update(self):
        if self.model.current_entry.is_dir():
            self.body = self.entry_list
            self.frame.set_body(self.entry_list)
        else:
            self.body = self.file_preview
            self.frame.set_body(self.file_preview)
        self.update_title()

    def update_title(self):
        mode = self.model.mode
        if mode == Mode.NORMAL:
            self.set_title_to_cwd()
        elif mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.box.set_title("assign key: choose entry")
        elif mode == Mode.ASSIGN_CHOOSE_KEY:
            self.box.set_title("assign key: choose new key")

    def set_title_to_cwd(self):
        cwd = self.model.current_entry.path
        if cwd.startswith(environment.home):
            cwd = "~" + cwd[len(environment.home):]
        self.box.set_title(cwd)

    def keypress(self, size, key):
        maxcol, maxrow = size
        try:
            if key == '/':
                if not self.frame.footer:
                    self.frame.footer = Filter(self.model, self.frame)
                self.frame.focus_position = 'footer'
            elif key == 'ctrl f':
                self.body.scroll(maxrow, valign='top')
            elif key == 'ctrl b':
                self.body.scroll(-maxrow, valign='top')
            elif key == 'ctrl d':
                self.body.scroll(maxrow // 2, valign='top')
            elif key == 'ctrl u':
                self.body.scroll(-(maxrow // 2), valign='top')

            elif self.model.mode == Mode.NORMAL:
                return self.handle_normal_keypress(size, key)
            else:
                return self.body.handle_assign_keypress(size, key)
        except PermissionError:
            app.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "PERMISSION DENIED"))
            return key
        except FileNotFoundError:
            app.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "FILE NOT FOUND"))
            return key

    def handle_normal_keypress(self, size, key):
        if key == '.':
            self.navigator.visit_parent()
            self.clear_filter()
        elif key == '~' or key == '`':
            self.navigator.visit_path(environment.home)
            self.clear_filter()
        elif key == 'backspace':  # also matches ctrl h
            self.navigator.visit_previous()
            self.clear_filter()
        elif key == 'ctrl l':
            self.navigator.visit_next()
            self.clear_filter()
        elif self.navigator.is_navigation_key(key):
            self.navigator.visit_child(key)
            self.clear_filter()
        elif key == 'enter':
            environment.append_to_cwd_pipe(self.navigator.history.cwd())
            raise urwid.ExitMainLoop()
        elif key == 'ctrl y':
            pyperclip.copy(self.model.current_entry.path)
        elif key == '=':
            self.body.enter_assign_mode(size)
        else:
            return key

    def clear_filter(self):
        if self.frame.footer:
            self.frame.footer.clear_filter()
