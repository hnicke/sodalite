import logging

from urwid import Text

from sodalite.core.entry import Entry
from sodalite.ui import graphics
from sodalite.ui.entrylist import List
from sodalite.ui.highlighting import HighlightedLine
from sodalite.util import topic

logger = logging.getLogger(__name__)


class FilePreview(List):
    def __init__(self) -> None:
        super().__init__()
        self.content: list[HighlightedLine] = []
        topic.filtered_file_content.connect(self.on_file_content_changed)
        topic.entry.connect(self.on_entry_changed)

    def on_file_content_changed(self, content: list[HighlightedLine]) -> None:
        if content != self.content:
            self.content = content
            with graphics.DRAW_LOCK:
                self.body.clear()
                self.body.extend([Text(line.numbered_content) for line in self.content])
                if len(self.content) > 0:
                    self.focus_position = 0
            graphics.redraw_if_external()

    def on_entry_changed(self, entry: Entry) -> None:
        if not entry.is_plain_text_file and entry.is_file:
            self.body.clear()
