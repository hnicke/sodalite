import logging
import os

from core import key as key_module
from core.key import Key
from util.observer import Observable
from .dirhistory import DirHistory
from .entry import Entry
from .entryaccess import EntryAccess

logger = logging.getLogger(__name__)


class Navigator:
    """Public interface of the core package.
    Clients (e.g., GUI) may use the navigator class for interaction
    """

    def __init__(self, history: DirHistory = DirHistory(), entry_access: EntryAccess = EntryAccess()):
        self.history = history
        self.entry_access = entry_access
        self.entry_notifier = Observable()
        self._current_entry = None
        self.current_entry = self.current()

    def current(self) -> Entry:
        """
        :return: The entry belonging to the current directory,
        or None in case the current directory does not exist anymore
        """
        path = self.history.cwd()
        entry = self.entry_access.retrieve_entry(path)
        _chdir(entry)
        return entry

    def is_navigation_key(self, key: str) -> bool:
        if key_module.is_navigation_key(key):
            return self.entry_access.is_possible(Key(key))
        return False

    def visit_child(self, key: str) -> Entry:
        """
        Visit entry that is child of current entry and whose key matches given key.
        :param key:
        :return: matching entry or current entry, if no match was found
        :raises: FileNotFoundError, PermissionError
        """
        try:
            entry = self.entry_access.get_entry_for_key(Key(key))
        except FileNotFoundError:
            # try to rescan dir
            self.current_entry = self.entry_access.retrieve_entry(self.history.cwd(), cache=False)
            raise FileNotFoundError
        if entry is None:
            entry = self.current()
        self.history.visit(entry.path)
        self.current_entry = entry
        _chdir(entry)
        return entry

    def visit_path(self, path: str) -> Entry:
        """
        Visit the file matching given path
        :param path: An absolute, canonical path describing a file
        :return:the matching entry
        :raises: PermissionError
        """
        self.history.visit(path)
        entry = self.entry_access.retrieve_entry(path)
        self.current_entry = entry
        _chdir(entry)
        return entry

    def visit_previous(self) -> Entry:
        path = self.history.backward()
        entry = self.entry_access.retrieve_entry(path)
        self.current_entry = entry
        _chdir(entry)
        return entry

    def visit_next(self) -> Entry:
        path = self.history.forward()
        entry = self.entry_access.retrieve_entry(path)
        self.current_entry = entry
        _chdir(entry)
        return entry

    def visit_parent(self) -> Entry:
        path = self.history.visit_parent()
        try:
            entry = self.entry_access.retrieve_entry(path)
            self.current_entry = entry
            _chdir(entry)
            return entry
        except FileNotFoundError:
            self.visit_previous()
            raise FileNotFoundError

    def assign_key(self, key: Key, path: str):
        """Assigns given key to given entry.
        if the new key is already taken by another entry on the same level, keys are swapped"""
        logger.info("Assigning key '{}' to entry '{}'".format(key, path))
        parent = self.entry_access.get_current()
        entry = parent.get_child_for_path(path)
        conflicting_entry = parent.get_child_for_key(key)
        old_key = entry.key
        entry.key = key
        self.entry_access.update_entry(entry)
        if conflicting_entry is not None:
            conflicting_entry.key = old_key
            self.entry_access.update_entry(conflicting_entry)
            logger.debug("Swapped key of conflicting entry '{}'".format(conflicting_entry))

    @property
    def current_entry(self):
        return self._current_entry

    @current_entry.setter
    def current_entry(self, entry: Entry):
        self._current_entry = entry
        self.entry_notifier.notify_all()


def _chdir(entry):
    if entry.is_dir():
        pwd = entry.path
    else:
        pwd = entry.dir
    os.chdir(pwd)
