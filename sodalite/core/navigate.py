import logging
import os
from pathlib import Path
from typing import Optional

from sodalite.core import key as key_module
from sodalite.core.entry import Entry
from sodalite.core.entryaccess import EntryAccess
from sodalite.core.history import History
from sodalite.core.key import Key
from sodalite.util import pubsub

logger = logging.getLogger(__name__)


def _sanitize(path: Path) -> Path:
    """
    If path exists, returns path. Else returns the first parent that exists.
    :raises FileNotFoundError as last resort
    """
    while not path.exists():
        if path == path.parent:
            raise FileNotFoundError()
        path = path.parent
    return path


def _chdir(entry: Entry) -> None:
    if entry.is_dir:
        pwd = entry.path
    else:
        pwd = entry.dir
    os.chdir(pwd)


class Navigator:
    """Public interface of the core package.
    Clients (e.g., GUI) may use the navigator class for interaction
    """

    def __init__(self, history: History = History.load(), entry_access: Optional[EntryAccess] = None):
        super().__init__()
        self.history = history
        self.entry_access = entry_access or EntryAccess()
        self._current_entry: Optional[Entry] = None
        pubsub.filesystem_connect(self.reload_current_entry)

    def current(self) -> Entry:
        """
        :return: The entry belonging to the current directory,
        If the current directory doesn't exist, returns the first existing parent
        or None in case the current directory does not exist anymore
        """
        path = _sanitize(Path(os.environ.get('PWD', '/')))
        entry = self.entry_access.retrieve_entry(path)
        _chdir(entry)
        return entry

    def is_navigation_key(self, key: str) -> bool:
        if key_module.is_navigation_key(key):
            return self.entry_access.is_possible(Key(key))
        return False

    def visit_child(self, key: Key) -> Entry:
        """
        Visit entry that is child of current entry and whose key matches given key.
        :param key:
        :return: matching entry or current entry, if no match was found
        :raises: FileNotFoundError, PermissionError
        """
        try:
            entry = self.entry_access.retrieve_entry_for_key(key)
        except FileNotFoundError:
            # try to rescan dir
            self.current_entry = self.entry_access.retrieve_entry(self.history.cwd(), cache=False)
            raise FileNotFoundError
        if entry is None:
            entry = self.current()
        return self._visit_entry(entry)

    def visit_path(self, path: Path, update_access: bool = True, update_history: bool = True) -> Entry:
        """
        Visit the file matching given path
        :param path: An absolute, canonical path describing a file
        :return:the matching entry
        :raises: PermissionError
        """
        try:
            entry = self.entry_access.retrieve_entry(path)
            return self._visit_entry(entry, update_access=update_access, update_history=update_history)
        except FileNotFoundError:
            return self.visit_path(path.parent, update_access=update_access, update_history=update_history)

    def _visit_entry(self, entry: Entry, update_access: bool = True, update_history: bool = True) -> Entry:
        if not entry.path.exists():
            return self.visit_path(entry.path.parent)
        if update_history:
            self.history.visit(entry.path)
        self.current_entry = entry
        if update_access:
            self.entry_access.access_now(entry)
        _chdir(entry)
        return entry

    def visit_previous(self) -> Entry:
        path = self.history.backward()
        entry = self.entry_access.retrieve_entry(path)
        return self._visit_entry(entry, update_access=False, update_history=False)

    def visit_next(self) -> Entry:
        path = self.history.forward()
        entry = self.entry_access.retrieve_entry(path)
        return self._visit_entry(entry, update_access=False, update_history=False)

    def visit_parent(self) -> Entry:
        path = self.history.cwd().parent
        entry = self.entry_access.retrieve_entry(path)
        return self._visit_entry(entry)

    def assign_key(self, key: Key, path: Path) -> None:
        """Assigns given key to given entry.
        if the new key is already taken by another entry on the same level, keys are swapped"""
        logger.info(f"Assigning key '{key}' to entry '{path}'")
        parent = self.entry_access.get_current()
        entry = parent.get_child_for_path(path)
        if entry is None:
            # TODO when could this happen?
            raise ValueError()
        conflicting_entry = parent.get_child_for_key(key)
        old_key = entry.key
        entry.key = key
        self.entry_access.update_entry(entry)
        if conflicting_entry is not None:
            # TODO the swap should be an atomic operation with above update
            conflicting_entry.key = old_key
            self.entry_access.update_entry(conflicting_entry)
            logger.debug(f"Swapped key of conflicting entry '{conflicting_entry}'")

    @property
    def current_entry(self) -> Entry:
        if not self._current_entry:
            raise Exception('Navigator not properly initialized')
        return self._current_entry

    @current_entry.setter
    def current_entry(self, entry: Entry) -> None:
        self._current_entry = entry
        pubsub.entry_send(entry)

    def reload_current_entry(self, *args: object) -> None:
        logger.info('Reloading current entry')
        self.current_entry = self.entry_access.retrieve_entry(_sanitize(self.current_entry.path), cache=False)
