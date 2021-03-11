import logging

import urwid

from sodalite.core.entry import Entry
from sodalite.core.navigate import Navigator
from sodalite.ui import theme, graphics
from sodalite.ui.entrylist import EntryList
from sodalite.ui.filepreview import FilePreview
from sodalite.ui.viewmodel import ViewModel
from sodalite.util import env, topic

logger = logging.getLogger(__name__)


class MainPane(urwid.WidgetWrap):  # type: ignore

    def __init__(self, model: ViewModel, navigator: Navigator) -> None:
        self.model = model
        self.navigator = navigator
        self.entry_list = EntryList(self, self.model, self.navigator)
        self.file_preview = FilePreview()
        self.body = self.entry_list
        self.frame = urwid.Frame(self.body)
        self.box = urwid.LineBox(urwid.AttrMap(self.frame, ''), title_align='left')
        self.box.title_widget.set_layout('right', 'clip')
        self.colored_box = theme.DynamicAttrMap(self.box)
        self.filter = self.frame.footer

        super().__init__(self.colored_box)
        topic.entry.connect(self.on_entry_changed)

    def on_entry_changed(self, entry: Entry) -> None:
        with graphics.DRAW_LOCK:
            if entry.is_dir:
                self.body = self.entry_list
                self.frame.set_body(self.entry_list)
            else:
                self.body = self.file_preview
                self.frame.set_body(self.file_preview)
            self._update_title(entry)
            graphics.redraw_if_external()

    def _update_title(self, entry: Entry) -> None:
        cwd = entry.path
        if cwd == env.HOME:
            title = '~'
        elif cwd.is_relative_to(env.HOME):
            title = f"~/{cwd.relative_to(env.HOME)}"
        else:
            title = str(cwd)
        self.box.set_title(title)
