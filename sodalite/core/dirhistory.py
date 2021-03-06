import atexit
import json
import logging
import os
from json import JSONDecodeError

from sodalite.util import environment

logger = logging.getLogger(__name__)

MAX_LENGTH = 50


# TODO refactor this class to use Path instead of strings everywhere
class DirHistory:
    """
    Keeps a history of visited files and offers methods for navigation within this history.
    Will never check if a file path is a valid file path.
    """

    def __init__(self, history: str, index: int = 0, persist: bool = False):
        assert history
        self._history = history
        self._current_index = index
        if persist:
            atexit.register(save, self)

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


def load(start_entry: str) -> DirHistory:
    logger.info('Load navigation history')
    if not os.path.isfile(environment.history_file):
        return DirHistory([start_entry], persist=True)
    with open(environment.history_file, 'r') as file:
        text = file.read()
        try:
            history: DirHistory = json.loads(text, object_hook=object_decoder)
            history._history.insert(history._current_index + 1, start_entry)
            history._current_index += 1
            return history
        except JSONDecodeError:
            return DirHistory([start_entry], persist=True)


def object_decoder(obj) -> DirHistory:
    try:
        return DirHistory(obj['_history'], obj['_current_index'], persist=True)
    except KeyError:
        logger.warning("Failed to load navigation history")
        raise JSONDecodeError


def save(history: DirHistory):
    history._truncate()
    logger.info('Persist navigation history')
    text = json.dumps(history.__dict__, indent=4)
    with open(environment.history_file, 'w') as file:
        file.write(text)
