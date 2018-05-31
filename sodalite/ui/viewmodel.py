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
        self.children = None
        self.file_content = None
        self.filter_string = ""
        self.filtered_children = []
        self.sorted_children = []
        self.navigator = navigator
        navigator.entry_notifier.register(self)

    def on_update(self):
        self.current_entry = self.navigator.current_entry
        self.children = list(self.current_entry.children)
        if self.current_entry.is_plain_text_file():
            self.file_content = self.current_entry.content

        self.sorted_children = sort(self.children)
        self.filter_string = ""
        self.filter("")

    def filter(self, filter_string: str):
        if filter_string[-1:] == "\\":
            return
        self.filtered_children.clear()
        p = re.compile(filter_string, re.IGNORECASE)
        for entry in self.sorted_children:
            if p.search(entry.name):
                self.filtered_children.append(entry)
        self.filter_string = filter_string
        self.notify_all()


def sort(entries: List[Entry]):
    sorted_entries = sorted(entries, key=lambda x: x.name)
    sorted_entries.sort(key=lambda x: x.is_dir(), reverse=True)
    sorted_entries.sort(key=lambda x: x.is_hidden())
    sorted_entries.sort(key=lambda x: x.key.value == "")
    sorted_entries.sort(key=lambda x: x.frequency, reverse=True)
    return sorted_entries
