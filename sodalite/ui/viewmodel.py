import logging
import re
import sre_constants
from enum import Enum
from sre_parse import Pattern
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


class Topic(Enum):
    MODE = 'mode'
    CURRENT_ENTRY = 'current_entry'
    ENTRIES = 'entries'
    FILTERED_FILE_CONTENT = 'filtered_file_content'


class ViewModel(Observable):
    def __init__(self, navigator: Navigator):
        super().__init__()
        self._mode = Mode.NORMAL
        self._current_entry: Entry = None
        self._entries = []
        self.file_content: List[HighlightedLine] = None
        self._filtered_file_content: List[HighlightedLine] = []
        self._filter_pattern: Pattern = re.compile('')
        self.navigator = navigator
        self._show_hidden_files = True
        navigator.entry_notifier.register(self.on_update)

    def on_update(self):
        self.current_entry = self.navigator.current_entry
        if self.current_entry.is_plain_text_file():
            self.file_content = list(highlighting.compute_highlighting(self.current_entry))
        else:
            self.file_content = None

        self._filter_pattern = re.compile('')
        self.process()

    def process(self):
        if self.current_entry.is_plain_text_file():
            self.filtered_file_content = self.filter_file_content()
        else:
            entries = list(self.current_entry.children)
            entries = self.filter_entry(entries)
            entries = self.filter_hidden_files(entries)
            entries = sort(entries)
            self.entries = entries

    def filter_entry(self, entries: List[Entry]) -> List[Entry]:
        return [entry for entry in entries if self.filter_pattern.search(entry.name)]

    def filter_file_content(self):
        return [line for line in self.file_content if line.matches(self.filter_pattern)]

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
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        self.notify_all(topic=Topic.MODE)

    @property
    def current_entry(self) -> Entry:
        return self._current_entry

    @current_entry.setter
    def current_entry(self, entry: Entry):
        self._current_entry = entry
        self.notify_all(topic=Topic.CURRENT_ENTRY)

    @property
    def entries(self) -> List[Entry]:
        return self._entries

    @entries.setter
    def entries(self, entries: List[Entry]):
        self._entries = entries
        self.notify_all(Topic.ENTRIES)

    @property
    def filtered_file_content(self) -> List[HighlightedLine]:
        return self._filtered_file_content

    @filtered_file_content.setter
    def filtered_file_content(self, content: List[HighlightedLine]):
        self._filtered_file_content = content
        self.notify_all(topic=Topic.FILTERED_FILE_CONTENT)


def sort(entries: List[Entry]):
    sorted_entries = sorted(entries, key=lambda x: x.name)
    sorted_entries.sort(key=lambda x: x.is_dir(), reverse=True)
    sorted_entries.sort(key=lambda x: x.is_hidden())
    sorted_entries.sort(key=lambda x: x.name_precedence)
    sorted_entries.sort(key=lambda x: x.rating, reverse=True)
    sorted_entries.sort(key=lambda x: x.key.value == "")
    return sorted_entries
