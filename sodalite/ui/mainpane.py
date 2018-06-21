import logging

import pyperclip
import urwid
from urwid import AttrSpec

from ui import theme, graphics
from ui.entrylist import EntryList
from ui.filepreview import FilePreview
from ui.filter import Filter
from ui.viewmodel import ViewModel, Mode
from util import environment
from util import keymap
from util.keymap import Action

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
        with graphics.DRAW_LOCK:
            if self.model.current_entry.is_dir():
                self.body = self.entry_list
                self.frame.set_body(self.entry_list)
            else:
                self.body = self.file_preview
                self.frame.set_body(self.file_preview)
            self.update_title()
            graphics.redraw_if_external()

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
        try:
            if key == '/':
                if not self.frame.footer:
                    self.frame.footer = Filter(self.model, self.frame)
                self.frame.focus_position = 'footer'
            elif self.model.mode == Mode.NORMAL:
                unhandled = self.keypress_normal(size, key)
                if unhandled:
                    return self.body.keypress(size, key)
            else:
                return self.body.keypress(size, key)
        except PermissionError:
            graphics.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "PERMISSION DENIED"))
        except FileNotFoundError:
            graphics.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "FILE NOT FOUND"))

    def keypress_normal(self, size, key):
        if key == '.':
            self.navigator.visit_parent()
            self.clear_filter()
        elif key == '~' or key == '`':
            self.navigator.visit_path(environment.home)
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_PREVIOUS, key):
            self.navigator.visit_previous()
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_NEXT, key):
            self.navigator.visit_next()
            self.clear_filter()
        elif self.navigator.is_navigation_key(key):
            self.navigator.visit_child(key)
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_ROOT, key):
            self.navigator.visit_path('/')
        elif keymap.matches(Action.EXIT, key):
            graphics.exit(cwd=self.navigator.history.cwd())
        elif keymap.matches(Action.YANK_CURRENT_PATH, key):
            self.yank_to_clipboard()
        elif keymap.matches(Action.ASSIGN_MODE, key):
            self.body.enter_assign_mode(size)
        else:
            return key

    def yank_to_clipboard(self):
        try:
            path = self.model.current_entry.path
            pyperclip.copy(path)
            logger.info(f"Yanked '{path} to system clipboard")
            graphics.notify(f"Yanked to clipboard", duration=1)
        except pyperclip.PyperclipException:
            logger.exception(f"Failed to yank current path '{path}'")
            graphics.notify("Failed to yank: system has no clipboard", duration=2)

    def clear_filter(self):
        if self.frame.footer:
            self.frame.footer.clear_filter()
