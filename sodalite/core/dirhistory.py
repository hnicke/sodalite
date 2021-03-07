import atexit
import json
import logging
import os
from pathlib import Path
from typing import List

from sodalite.util import env

logger = logging.getLogger(__name__)

MAX_LENGTH = 50

_HISTORY_FILE = env.USER_DATA / 'history.json'


class HistoryLoadException(Exception):
    pass


# TODO refactor this class to use Path instead of strings everywhere
class DirHistory:
    """
    Keeps a history of visited files and offers methods for navigation within this history.
    Will never check if a file path is a valid file path.
    """

    def __init__(self, history: List[str] = None, index: int = 0, persist: bool = False):
        self._history = history or [str(env.HOME)]
        self._current_index = index
        if persist:
            atexit.register(self.save)

    @classmethod
    def load(cls, file: Path = _HISTORY_FILE) -> 'DirHistory':
        if file.is_file():
            json_history = file.read_text()
            try:
                history: DirHistory = json.loads(json_history, object_hook=_object_decoder)
                logger.debug(f"Loaded navigation history from '{file}'")
                return history
            except HistoryLoadException:
                return DirHistory(persist=True)
        else:
            return DirHistory(persist=True)

    def save(self, file: Path = _HISTORY_FILE):
        self._truncate()
        json_history = json.dumps(self.__dict__, indent=4)
        file.write_text(json_history)
        logger.debug(f"Persisted navigation history to '{file}'")

    def cwd(self) -> str:
        """
        :return: The current absolute, canonical path
        """
        return self._history[self._current_index]

    def visit(self, path: str):
        """
        Adds given path to the dir history as most recent entry.
        Does nothing if the most recent entry is the same as given path.
        :param path: An absolute, canonical file path. No checks regarding existence of this file are made
        """
        if self.cwd() != path:
            logger.info("Visiting '{}'".format(path))
            self.__discard_future()
            self._history.append(path)
            self._current_index += 1

    def __discard_future(self):
        del self._history[self._current_index + 1:]

    def visit_parent(self) -> str:
        """
        Adds the parent file (relative to the current file) to the history.
        Does not append file to history if the most recent entry is the same as its parent entry.
        :return: The absolute, canonical file path of the current file's parent
        """
        parent = os.path.dirname(self.cwd())
        self.visit(parent)
        return self.cwd()

    def backward(self) -> str:
        """
        Goes one step backwards in history
        :return: The previously visited file path.
        If there is no previously visited file path, returns the current file path."""
        if self._current_index > 0:
            self._current_index -= 1
            path = self.cwd()
            logger.info("Going back to '{}'".format(path))
            return path
        else:
            return self.cwd()

    def forward(self) -> str:
        """
        Replays one step in history (redo). Returns current file path, if this is not possible
        :return: The next file path, if exists - or the current file path
        """
        if len(self._history) > self._current_index + 1:
            self._current_index += 1
            path = self.cwd()
            logger.info("Going forward to '{}'".format(path))
            return path
        else:
            return self.cwd()

    def _truncate(self):
        """
        In case the history is longer than MAX_LENGTH, discards parts of it.
        """
        if len(self._history) > MAX_LENGTH:
            half = MAX_LENGTH // 2
            lower = max(self._current_index - half, 0)
            upper = min(lower + MAX_LENGTH, len(self._history))
            lower = min(upper - MAX_LENGTH, lower)
            self._history = self._history[lower:upper]
            self._current_index -= lower

    def __repr__(self) -> str:
        return str(self._history)

    def __eq__(self, other):
        return isinstance(other, DirHistory) and self.__dict__ == other.__dict__


def _object_decoder(obj) -> DirHistory:
    try:
        return DirHistory(obj['_history'], obj['_current_index'], persist=True)
    except KeyError as e:
        logger.warning(f"Failed to load navigation history: {e}")
        raise HistoryLoadException()
