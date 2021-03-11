import logging
import os
import time
from pathlib import Path
from typing import Optional

from sodalite.core import dao
from sodalite.core import hook
from sodalite.core.key import Key
from .entry import Entry

logger = logging.getLogger(__name__)


class EntryAccess:

    def __init__(self) -> None:
        # TODO make this non optional
        self._current_entry: Optional[Entry] = None

    def get_current(self) -> Entry:
        if self._current_entry is None:
            raise ValueError()
        return self._current_entry

    def retrieve_entry(self, path: Path, populate_children: bool = True, cache: bool = True) -> Entry:
        """
        Returns an entry matching given path.
        :param path: the absolute, canonical path to a file
        :param populate_children: If true, loads children from database
        :return: the matching entry
        :raise: FileNotFoundError
        """

        if cache and self._current_entry is not None and path == self._current_entry.path:
            return self._current_entry
        entry = Entry(path)
        entry.hooks = hook.get_hooks(entry)
        if populate_children:
            check_permission(entry)
            self.__populate_children(entry)
            self._current_entry = entry
        return entry

    def __populate_children(self, entry: Entry) -> None:
        if not entry.is_dir:
            return
        entry.children = [Entry(Path(x), parent=entry) for x in entry.path.glob('*')]
        dao.inject_data(entry)

    def retrieve_entry_for_key(self, key: Key) -> Optional[Entry]:
        """
        Returns an entry matching given key.
        :param key: the key of the target entry
        :return: the matching entry on None, if no entry with given key exists
        :raise: FileNotFoundError, PermissionError
        """
        if not self._current_entry:
            raise ValueError()
        entry = self._current_entry.get_child_for_key(key)
        if not entry:
            return None
        if not entry.exists:
            raise FileNotFoundError()
        check_permission(entry)
        entry.hooks = hook.get_hooks(entry)
        # TODO removed update of frequency. add again somewhere else!
        self.__populate_children(entry)
        self._current_entry = entry
        return entry

    def update_entry(self, entry: Entry) -> None:
        dao.update_entry(entry)

    def is_possible(self, key: Key) -> bool:
        if self._current_entry is None:
            raise ValueError()
        return self._current_entry.get_child_for_key(key) is not None

    def access_now(self, entry: Entry) -> None:
        """Adds a new access to given entry"""
        if not dao.entry_exists(entry.path):
            dao.insert_entry(entry)
        access = int(time.time() * 1000)
        entry.access_history.append(access)
        dao.insert_access(entry.path, access)


def check_permission(entry: Entry) -> None:
    if entry.is_dir:
        access = os.access(entry.path, os.X_OK)
    else:
        access = os.access(entry.path, os.R_OK)
    if not access:
        logger.info(f"Cannot visit {entry.path}: Permission denied")
        raise PermissionError
