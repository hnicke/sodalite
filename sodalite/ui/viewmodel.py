import re
from typing import List

from core.entry import Entry


class ViewModel:
    def __init__(self, entry: Entry):
        self.current_entry = None
        self.children = None
        self.actions = None
        self.filter_string = ""
        self.filtered_entries = []
        self.update(entry)

    def update(self, entry: Entry):
        self.current_entry = entry
        self.children = entry.children
        sort(self.children)

        self.actions = entry.actions
        self.filter_string = ""
        self.filter("")

    def filter(self, filter_string: str):
        if filter_string[-1:] == "\\":
            return
        self.filtered_entries.clear()
        p = re.compile(filter_string, re.IGNORECASE)
        for entry in self.children:
            if p.search(entry.name):
                self.filtered_entries.append(entry)
        self.filter_string = filter_string

    def get_filtered_entries(self) -> List[Entry]:
        return self.filtered_entries


def sort(entries: List[Entry]):
    entries.sort(key=lambda x: x.name)
    entries.sort(key=lambda x: x.is_dir(), reverse=True)
    entries.sort(key=lambda x: x.is_hidden())
    entries.sort(key=lambda x: x.key.value == "")
    entries.sort(key=lambda x: x.frequency, reverse=True)
