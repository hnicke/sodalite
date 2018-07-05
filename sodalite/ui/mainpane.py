import logging

import pyperclip
import urwid
from urwid import AttrSpec

import ui.notify
from core.navigator import Navigator
from ui import theme, graphics, notify, viewmodel
from ui.entrylist import EntryList
from ui.filepreview import FilePreview
from ui.filter import Filter
from ui.viewmodel import ViewModel, Mode, Topic
from util import environment
from util import keymap
from util.keymap import Action

logger = logging.getLogger(__name__)


class MainPane(urwid.WidgetWrap):

    def __init__(self, model: ViewModel, navigator: Navigator):
        self.model = model
        self.navigator = navigator
        self.entry_list = EntryList(self, self.model, self.navigator)
        self.file_preview = FilePreview(model)
        self.body = self.entry_list
        self.frame = urwid.Frame(self.body)
        self.box = urwid.LineBox(self.frame, title_align='left')
        self.box.title_widget.set_layout('right', 'clip')
        self.colored_box = theme.DynamicAttrMap(self.box)
        viewmodel.global_mode.register(self.on_mode_changed, topic=Topic.MODE)
        self.model.register(self.on_entry_changed, topic=Topic.CURRENT_ENTRY)

        super().__init__(self.colored_box)

    def on_entry_changed(self, model):
        with graphics.DRAW_LOCK:
            if model.current_entry.is_dir():
                self.body = self.entry_list
                self.frame.set_body(self.entry_list)
            else:
                self.body = self.file_preview
                self.frame.set_body(self.file_preview)
            self.set_title_to_cwd(model)
            graphics.redraw_if_external()

    def on_mode_changed(self, model):
        self.trigger_notifications(model)

    def trigger_notifications(self, model):
        if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY:
            notify.show("choose entry", duration=0)
        elif viewmodel.global_mode == Mode.ASSIGN_CHOOSE_KEY:
            notify.show("choose new key", duration=0)
        elif viewmodel.global_mode == Mode.NORMAL:
            notify.clear()

    def set_title_to_cwd(self, model):
        cwd = model.current_entry.path
        if cwd.startswith(environment.home):
            cwd = "~" + cwd[len(environment.home):]
        self.box.set_title(cwd)

    def keypress(self, size, key):
        try:
            if key == '/':
                if not self.frame.footer:
                    self.frame.footer = Filter(self.model, self.frame)
                self.frame.focus_position = 'footer'
            elif viewmodel.global_mode == Mode.NORMAL:
                unhandled = self.keypress_normal(size, key)
                if unhandled:
                    return self.body.keypress(size, key)
            else:
                return self.body.keypress(size, key)
        except PermissionError:
            ui.notify.show((AttrSpec(theme.forbidden + ',bold', '', colors=16), "PERMISSION DENIED"))
        except FileNotFoundError:
            ui.notify.show((AttrSpec(theme.forbidden + ',bold', '', colors=16), "FILE NOT FOUND"))

    def keypress_normal(self, size, key):
        if self.navigator.is_navigation_key(key):
            self.navigator.visit_child(key)
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_PARENT, key):
            self.navigator.visit_parent()
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_HOME, key):
            self.navigator.visit_path(environment.home)
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_ROOT, key):
            self.navigator.visit_path('/')
        elif keymap.matches(Action.GO_TO_PREVIOUS, key):
            self.navigator.visit_previous()
            self.clear_filter()
        elif keymap.matches(Action.GO_TO_NEXT, key):
            self.navigator.visit_next()
            self.clear_filter()
        elif keymap.matches(Action.EXIT, key):
            graphics.exit(cwd=self.navigator.history.cwd())
        elif keymap.matches(Action.YANK_CURRENT_PATH, key):
            self.yank_to_clipboard()
        else:
            return key

    def yank_to_clipboard(self):
        try:
            path = self.model.current_entry.path
            pyperclip.copy(path)
            logger.info(f"Yanked '{path} to system clipboard")
            ui.notify.show(f"Yanked to clipboard", duration=1)
        except pyperclip.PyperclipException:
            logger.exception(f"Failed to yank current path '{path}'")
            ui.notify.show("Failed to yank: system has no clipboard", duration=2)

    def clear_filter(self):
        if self.frame.footer:
            self.frame.footer.clear_filter()
