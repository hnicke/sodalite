import logging

import urwid

from sodalite.core.navigate import Navigator
from sodalite.ui import theme, graphics
from sodalite.ui.entrylist import EntryList
from sodalite.ui.filepreview import FilePreview
from sodalite.ui.viewmodel import ViewModel, Topic
from sodalite.util import env

logger = logging.getLogger(__name__)


class MainPane(urwid.WidgetWrap):

    def __init__(self, model: ViewModel, navigator: Navigator):
        self.model = model
        self.navigator = navigator
        self.entry_list = EntryList(self, self.model, self.navigator)
        self.file_preview = FilePreview(model)
        self.body = self.entry_list
        self.frame = urwid.Frame(self.body)
        self.box = urwid.LineBox(urwid.AttrMap(self.frame, ''), title_align='left')
        self.box.title_widget.set_layout('right', 'clip')
        self.colored_box = theme.DynamicAttrMap(self.box)
        self.filter = self.frame.footer
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

    def set_title_to_cwd(self, model):
        cwd = model.current_entry.path
        if cwd.startswith(str(env.home)):
            cwd = "~" + cwd[len(str(env.home)):]
        self.box.set_title(cwd)
