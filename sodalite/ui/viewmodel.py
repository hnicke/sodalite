import logging
import re
from enum import Enum
from typing import List

from core.entry import Entry
from core.navigator import Navigator
from ui import highlighting
from ui.highlighting import HighlightedLine
from util.observer import Observable

logger = logging.getLogger(__name__)


class Mode(Enum):
    NORMAL = 1
    ASSIGN_CHOOSE_ENTRY = 2
    ASSIGN_CHOOSE_KEY = 3


class ViewModel(Observable):
    def __init__(self, navigator: Navigator):
        super().__init__()
        self.mode = Mode.NORMAL
        self.current_entry: Entry = None
        self.file_content: List[HighlightedLine] = None
        self.filtered_file_content: List[HighlightedLine] = None
        self._filter_string = ""
        self.navigator = navigator
        self._show_hidden_files = True
        self.entries = []
        navigator.entry_notifier.register(self)

    def on_update(self):
        self.current_entry = self.navigator.current_entry
        if self.current_entry.is_plain_text_file():
            self.file_content = list(highlighting.compute_highlighting(self.current_entry))
        else:
            self.file_content = None

        self._filter_string = ""
        self.process()

    def process(self):
        if self.current_entry.is_plain_text_file():
            self.filtered_file_content = self.filter_file_content()
            self.notify_all()
        else:
            entries = list(self.current_entry.children)
            entries = self.filter_regexp(entries)
            entries = self.filter_hidden_files(entries)
            entries = sort(entries)
            self.entries = entries
            self.notify_all()

    def filter_regexp(self, entries: List[Entry]) -> List[Entry]:
        p = self.get_filter_pattern()
        return [entry for entry in entries if p.search(entry.name)]

    def filter_file_content(self):
        pattern = self.get_filter_pattern()
        return [line for line in self.file_content if line.matches(pattern)]

    def get_filter_pattern(self):
        return re.compile(self.filter_string, re.IGNORECASE)

    def filter_hidden_files(self, entries: List[Entry]) -> List[Entry]:
        if self.show_hidden_files:
            return entries
        else:
            return [x for x in entries if x.is_hidden() is False]

    @property
    def show_hidden_files(self) -> bool:
        return self._show_hidden_files

    @show_hidden_files.setter
    def show_hidden_files(self, show: bool):
        if show != self._show_hidden_files:
            self._show_hidden_files = show
            self.process()

    @property
    def filter_string(self) -> str:
        return self._filter_string

    @filter_string.setter
    def filter_string(self, string: str):
        self._filter_string = string
        self.process()


def sort(entries: List[Entry]):
    sorted_entries = sorted(entries, key=lambda x: x.name)
    sorted_entries.sort(key=lambda x: x.is_dir(), reverse=True)
    sorted_entries.sort(key=lambda x: x.is_hidden())
    sorted_entries.sort(key=lambda x: x.rating, reverse=True)
    sorted_entries.sort(key=lambda x: x.key.value == "")
    return sorted_entries
