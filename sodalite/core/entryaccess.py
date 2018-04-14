import logging
import os

from core import entrydao
from core import hook
from core.key import Key
from .entry import Entry

logger = logging.getLogger(__name__)


class EntryAccess:

    def __init__(self):
        self.__current_entry = None

    def get_current(self):
        return self.__current_entry

    def retrieve_entry(self, path: str, populate_children=True) -> [Entry, None]:
        """
        Returns an entry matching given path.
        :param path: the absolute, canonical path to a file
        :return: the matching entry or None, if file does not exist
        """

        if self.is_cached(path):
            return self.__current_entry
        try:
            entry = Entry(path)
            entry.hooks = hook.get_hooks(entry)
            if populate_children:
                check_permission(entry)
                self.__populate_children(entry)
                self.__current_entry = entry
            return entry
        except FileNotFoundError:
            return None

    def is_cached(self, path: str):
        return self.__current_entry is not None and path == self.__current_entry

    def __populate_children(self, entry: Entry):
        entries = {}
        if not entry.is_dir():
            return entries
        with os.scandir(entry.realpath) as dir_entries:
            entry.__path_to_child = {}
            entry.children = list(map(lambda x: Entry(x.path, parent=entry), dir_entries))
        entrydao.inject_data(entry)

    def get_entry_for_key(self, key: Key) -> Entry:
        """
        Returns an entry matching given key.
        If a match was found, updates the entries frequency.
        :param key: the key of the target entry
        :return: the matching entry on None, if no entry with given key exists
        """
        entry = self.__current_entry.get_child_for_key(key)
        entry.hooks = hook.get_hooks(entry)
        check_permission(entry)
        entry.frequency += 1
        entrydao.update_entry(entry)
        self.__populate_children(entry)
        self.__current_entry = entry
        return entry

    def update_entry(self, entry: Entry):
        entrydao.update_entry(entry)

    def is_possible(self, key: Key):
        return self.__current_entry.get_child_for_key(key) is not None


def check_permission(entry: Entry):
    if entry.is_dir():
        access = os.access(entry.path, os.X_OK)
    else:
        access = os.access(entry.path, os.R_OK)
    if not access:
        logger.info(f"Cannot visit {entry.path}: Permission denied")
        raise PermissionError
