import logging
import os
import time

from core import entrydao
from core import hook
from core.key import Key
from .entry import Entry, Access

logger = logging.getLogger(__name__)


class EntryAccess:

    def __init__(self):
        self.__current_entry = None

    def get_current(self):
        return self.__current_entry

    def retrieve_entry(self, path: str, populate_children=True, cache=True) -> Entry:
        """
        Returns an entry matching given path.
        :param path: the absolute, canonical path to a file
        :return: the matching entry
        :raise: FileNotFoundError
        """

        if cache and self.is_cached(path):
            return self.__current_entry
        entry = Entry(path)
        entry.hooks = hook.get_hooks(entry)
        if populate_children:
            check_permission(entry)
            self.__populate_children(entry)
            self.__current_entry = entry
        return entry

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

    def retrieve_entry_for_key(self, key: Key) -> Entry:
        """
        Returns an entry matching given key.
        :param key: the key of the target entry
        :return: the matching entry on None, if no entry with given key exists
        :raise: FileNotFoundError, PermissionError
        """
        entry = self.__current_entry.get_child_for_key(key)
        if not entry.exists():
            raise FileNotFoundError
        check_permission(entry)
        entry.hooks = hook.get_hooks(entry)
        # TODO removed update of frequency. add again somewhere else!
        self.__populate_children(entry)
        self.__current_entry = entry
        return entry

    def update_entry(self, entry: Entry):
        entrydao.update_entry(entry)

    def is_possible(self, key: Key):
        return self.__current_entry.get_child_for_key(key) is not None

    def access_now(self, entry):
        """Adds a new access to given entry"""
        access = Access(time.time())
        entry.access_history.append(access)
        entrydao.insert_access(entry.path, access)


def check_permission(entry: Entry):
    if entry.is_dir():
        access = os.access(entry.path, os.X_OK)
    else:
        access = os.access(entry.path, os.R_OK)
    if not access:
        logger.info(f"Cannot visit {entry.path}: Permission denied")
        raise PermissionError
