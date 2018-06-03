import re
from enum import Enum
from typing import List

from core.entry import Entry
from core.navigator import Navigator
from util.observer import Observable


class Mode(Enum):
    NORMAL = 1
    ASSIGN_CHOOSE_ENTRY = 2
    ASSIGN_CHOOSE_KEY = 3


class ViewModel(Observable):
    def __init__(self, navigator: Navigator):
        super().__init__()
        self.mode = Mode.NORMAL
        self.current_entry: Entry = None
        self._unprocessed_children = None
        self.file_content = None
        self._filter_string = ""
        self.navigator = navigator
        self._show_hidden_files = True
        self.entries = []
        navigator.entry_notifier.register(self)

    def on_update(self):
        self.current_entry = self.navigator.current_entry
        self._unprocessed_children = self.current_entry.children
        if self.current_entry.is_plain_text_file():
            self.file_content = self.current_entry.content
        else:
            self.file_content = None

        self._filter_string = ""
        self.process()

    def process(self):
        entries = list(self._unprocessed_children)
        entries = self.filter_regexp(entries)
        entries = self.filter_hidden_files(entries)
        entries = sort(entries)
        self.entries = entries
        self.notify_all()

    def filter_regexp(self, entries: List[Entry]) -> List[Entry]:
        if self.filter_string[-1:] == "\\":
            return entries
        filtered = []
        p = re.compile(self.filter_string, re.IGNORECASE)
        for entry in entries:
            if p.search(entry.name):
                filtered.append(entry)
        return filtered

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
    sorted_entries.sort(key=lambda x: x.frequency, reverse=True)
    sorted_entries.sort(key=lambda x: x.key.value == "")
    return sorted_entries
