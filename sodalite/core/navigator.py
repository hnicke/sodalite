import logging
import os

from core import key as key_module
from core.entrywatcher import EntryWatcher
from core.key import Key
from util.observer import Observable
from .entry import Entry
from .entryaccess import EntryAccess

logger = logging.getLogger(__name__)


class Navigator(Observable):
    """Public interface of the core package.
    Clients (e.g., GUI) may use the navigator class for interaction
    """

    def __init__(self, history, entry_access: EntryAccess = EntryAccess()):
        super().__init__()
        self.history = history
        self.entry_access = entry_access
        self._current_entry = None
        self.register(EntryWatcher(self).on_update, immediate_update=False)
        self.current_entry = self.current()

    def current(self) -> Entry:
        """
        :return: The entry belonging to the current directory,
        or None in case the current directory does not exist anymore
        """
        path = self.history.cwd()
        entry = self.entry_access.retrieve_entry(path)
        self._chdir(entry)
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
            entry = self.entry_access.retrieve_entry_for_key(Key(key))
        except FileNotFoundError:
            # try to rescan dir
            self.current_entry = self.entry_access.retrieve_entry(self.history.cwd(), cache=False)
            raise FileNotFoundError
        if entry is None:
            entry = self.current()
        self.history.visit(entry.path)
        self.current_entry = entry
        self._access(entry)
        self._chdir(entry)
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
        self._access(entry)
        self._chdir(entry)
        return entry

    def visit_previous(self) -> Entry:
        path = self.history.backward()
        entry = self.entry_access.retrieve_entry(path)
        self.current_entry = entry
        self._chdir(entry)
        return entry

    def visit_next(self) -> Entry:
        path = self.history.forward()
        entry = self.entry_access.retrieve_entry(path)
        self.current_entry = entry
        self._chdir(entry)
        return entry

    def visit_parent(self) -> Entry:
        path = self.history.visit_parent()
        try:
            entry = self.entry_access.retrieve_entry(path)
            if not entry.path == self.current_entry.path:
                self.current_entry = entry
                self._chdir(entry)
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

    def _access(self, entry: Entry):
        """Adds an access to given entry"""
        self.entry_access.access_now(entry)

    def _chdir(self, entry):
        if entry.is_dir():
            pwd = entry.path
        else:
            pwd = entry.dir
        os.chdir(pwd)

    @property
    def current_entry(self):
        return self._current_entry

    @current_entry.setter
    def current_entry(self, entry: Entry):
        self._current_entry = entry
        self.notify_all()

    def reload_current_entry(self):
        try:
            self.current_entry = self.entry_access.retrieve_entry(self.current_entry.path, cache=False)
        except FileNotFoundError:
            self.recursive_try_visit(self.current_entry.dir)

    def recursive_try_visit(self, path):
        try:
            self.visit_path(path)
        except FileNotFoundError:
            self.recursive_try_visit(os.path.pardir(path))
