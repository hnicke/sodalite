import re
from typing import List

from core.entry import Entry
from core.navigator import Navigator
from mylogger import logger
from util.observer import Observable


class ViewModel(Observable):
    def __init__(self, navigator: Navigator):
        super().__init__()
        self.in_assign_mode = False
        self.current_entry = None
        self.children = None
        self.hooks = None
        self.filter_string = ""
        self.filtered_children = []
        self.sorted_children = []
        self.navigator = navigator
        navigator.entry_notifier.register(self)

    def update(self):
        self.current_entry = self.navigator.current_entry
        self.children = list(self.current_entry.children)
        self.hooks = [hook for hook in self.current_entry.hooks if hook.label is not None]

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
