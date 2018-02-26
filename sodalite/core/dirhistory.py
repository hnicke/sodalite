import logging
import os

logger = logging.getLogger(__name__)


class DirHistory:
    """
    Keeps a history of visited files and offers methods for navigation within this history.
    Will never check if a file path is a valid file path.
    """

    def __init__(self):
        self.__history = []
        self.__history.append(os.getcwd())
        self.__current_index = 0

    def cwd(self) -> str:
        """
        :return: The current absolute, canonical path
        """
        return self.__history[self.__current_index]

    def visit(self, path: str):
        """
        Adds given path to the dir history as most recent entry.
        Does nothing if the most recent entry is the same as given path.
        :param path: An absolute, canonical file path. No checks regarding existence of this file are made
        """
        if self.cwd() != path:
            logger.info("Visiting '{}'".format(path))
            self.__discard_future()
            self.__history.append(path)
            self.__current_index += 1

    def __discard_future(self):
        del self.__history[self.__current_index + 1:]

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
        if self.__current_index > 0:
            self.__current_index -= 1
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
        if len(self.__history) > self.__current_index + 1:
            self.__current_index += 1
            path = self.cwd()
            logger.info("Going forward to '{}'".format(path))
            return path
        else:
            return self.cwd()
