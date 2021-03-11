import logging
import re
import sre_constants
from enum import Enum
from re import Pattern
from typing import Optional

from sodalite.core.entry import Entry
from sodalite.ui import highlighting
from sodalite.ui.highlighting import HighlightedLine
from sodalite.util import topic

logger = logging.getLogger(__name__)


class Mode(Enum):
    NAVIGATE = 1
    ASSIGN_CHOOSE_ENTRY = 2
    ASSIGN_CHOOSE_KEY = 3
    OPERATE = 4


ANY_ASSIGN_MODE = (Mode.ASSIGN_CHOOSE_KEY, Mode.ASSIGN_CHOOSE_ENTRY)


class GlobalMode:

    def __init__(self):
        super().__init__()
        self.mode = Mode.NAVIGATE

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode: Mode):
        self._mode = mode
        topic.mode.send(self._mode)

    def __eq__(self, other):
        return self._mode == other or super.__eq__(self, other)


global_mode = GlobalMode()


class ViewModel:

    def __init__(self) -> None:
        super().__init__()
        self._current_entry: Optional[Entry] = None
        self._entries: list[Entry] = []
        self.file_content: Optional[list[HighlightedLine]] = None
        self._filtered_file_content: list[HighlightedLine] = []
        self._filter_pattern: Pattern = re.compile('')
        self._show_hidden_files = True
        topic.entry.connect(self.on_navigated)

    def on_navigated(self, entry: Entry):
        self.current_entry = entry
        if self.current_entry.is_plain_text_file:
            self.file_content = list(highlighting.compute_highlighting(self.current_entry))
        else:
            self.file_content = None

        self._filter_pattern = re.compile('')
        self.process()

    def process(self):
        if self.current_entry.is_plain_text_file:
            self.filtered_file_content = self.filter_file_content()
        else:
            entries = list(self.current_entry.children)
            entries = self.filter_entry(entries)
            entries = self.filter_hidden_files(entries)
            entries = sort(entries)
            self.entries = entries

    def filter_entry(self, entries: list[Entry]) -> list[Entry]:
        return [entry for entry in entries if self.filter_pattern.search(entry.name)]

    def filter_file_content(self):
        return [line for line in self.file_content if line.matches(self.filter_pattern)]

    def filter_hidden_files(self, entries: list[Entry]) -> list[Entry]:
        if self.show_hidden_files:
            return entries
        else:
            return [x for x in entries if not x.is_hidden]

    @property
    def show_hidden_files(self) -> bool:
        return self._show_hidden_files

    @show_hidden_files.setter
    def show_hidden_files(self, show: bool):
        if show != self._show_hidden_files:
            self._show_hidden_files = show
            self.process()

    @property
    def filter_pattern(self) -> Pattern:
        return self._filter_pattern

    @filter_pattern.setter
    def filter_pattern(self, pattern: str):
        try:
            self._filter_pattern = re.compile(pattern, re.IGNORECASE)
            self.process()
        except sre_constants.error:
            # .e.g gets thrown when string ends with '\' (user is about to escape a char)
            pass

    @property
    def current_entry(self) -> Entry:
        if not self._current_entry:
            raise Exception('Model was not properly initialized')
        return self._current_entry

    @current_entry.setter
    def current_entry(self, entry: Entry):
        self._current_entry = entry

    @property
    def entries(self) -> list[Entry]:
        return self._entries

    @entries.setter
    def entries(self, entries: list[Entry]):
        self._entries = entries
        topic.entry_list.send(entries)

    @property
    def filtered_file_content(self) -> list[HighlightedLine]:
        return self._filtered_file_content

    @filtered_file_content.setter
    def filtered_file_content(self, content: list[HighlightedLine]):
        self._filtered_file_content = content
        topic.filtered_file_content.send(content)


def sort(entries: list[Entry]):
    sorted_entries = sorted(entries, key=lambda x: x.name)
    sorted_entries.sort(key=lambda x: x.is_dir, reverse=True)
    sorted_entries.sort(key=lambda x: x.is_hidden)
    sorted_entries.sort(key=lambda x: x.name_precedence)
    sorted_entries.sort(key=lambda x: x.rating, reverse=True)
    sorted_entries.sort(key=lambda x: x.key.value == "")
    return sorted_entries
