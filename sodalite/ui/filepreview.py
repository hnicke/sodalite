import logging

from urwid import Text

from ui import graphics
from ui.entrylist import List
from ui.viewmodel import ViewModel

logger = logging.getLogger(__name__)


class FilePreview(List):
    def __init__(self, model):
        super().__init__()
        self.content = []
        self.model: ViewModel = model
        self.model.register(self)

    def on_update(self):
        if self.model.filtered_file_content != self.content:
            self.content = self.model.filtered_file_content
            with graphics.DRAW_LOCK:
                self.body.clear()
                self.body.extend([Text(line.numbered_content) for line in self.content])
                if len(self.content) > 0:
                    self.focus_position = 0
