import logging

import urwid

from core.navigator import Navigator
from ui import theme, graphics, notify, viewmodel
from ui.entrylist import EntryList
from ui.filepreview import FilePreview
from ui.viewmodel import ViewModel, Mode, Topic
from util import environment

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
        self.filter = self.frame.footer
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
        elif viewmodel.global_mode == Mode.NAVIGATE:
            notify.clear()

    def set_title_to_cwd(self, model):
        cwd = model.current_entry.path
        if cwd.startswith(environment.home):
            cwd = "~" + cwd[len(environment.home):]
        self.box.set_title(cwd)
