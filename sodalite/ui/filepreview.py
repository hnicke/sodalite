import logging

from urwid import Text

from ui import graphics
from ui.entrylist import List
from ui.viewmodel import Topic

logger = logging.getLogger(__name__)


class FilePreview(List):
    def __init__(self, model):
        super().__init__()
        self.content = []
        model.register(self.on_file_content_changed, Topic.FILTERED_FILE_CONTENT, immediate_update=False)
        model.register(self.on_entry_changed, Topic.CURRENT_ENTRY)

    def on_file_content_changed(self, model):
        if model.filtered_file_content != self.content:
            self.content = model.filtered_file_content
            with graphics.DRAW_LOCK:
                self.body.clear()
                self.body.extend([Text(line.numbered_content) for line in self.content])
                if len(self.content) > 0:
                    self.focus_position = 0
            graphics.redraw_if_external()

    def on_entry_changed(self, model):
        current = model.current_entry
        if not current.is_plain_text_file() and current.is_file():
            self.body.clear()
