import os
import stat
from _ast import List
from enum import Enum
from typing import Dict, Iterable

from binaryornot.check import is_binary

from core.actionhook import Action
from .key import Key


class EntryType(Enum):
    DIRECTORY = 1
    FILE = 2
    SYMLINK = 3
    FIFO = 4
    SOCKET = 5
    BLOCK_DEVICE = 6
    CHARACTER_DEVICE = 7


class Entry:
    """
    defines the entry class which represents a file or directory
    """

    def __init__(self, path: str, parent: 'Entry' = None, key: Key = Key(''),
                 frequency=0):
        """
        :param path: the absolute, canonical path of this entry
        """
        self.path = path
        self.__parent = parent
        self.dir, self.name = os.path.split(path)
        self._key = key

        self._children: List['Entry'] = []
        self.path_to_child: Dict[str, Entry] = {}
        self.key_to_child: Dict[Key, Entry] = {}

        self.frequency = frequency
        self.__is_plain_text_file = None
        self.actions: List[Action] = []
        self.stat = os.lstat(path)
        self.size = self.stat.st_size >> 10
        self.permissions = oct(self.stat.st_mode)[-3:]
        self.type = detect_type(self.stat.st_mode)
        if self.is_link():
            self.realpath = os.readlink(path)
        else:
            self.realpath = path

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children: Iterable['Entry']):
        self._children = children
        self.path_to_child.clear()
        self.key_to_child.clear()
        for entry in children:
            self.path_to_child[entry.path] = entry

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key: Key):
        self._key = key
        if self.__parent is not None:
            self.__parent.key_to_child[key] = self

    def get_child_for_key(self, key: Key) -> 'Entry' or None:
        return self.key_to_child.get(key, None)

    def get_child_for_path(self, path: str) -> 'Entry' or None:
        return self.path_to_child.get(path, None)

    def __str__(self):
        return "[path:{}, key:{}, type:{}, frequency:{}]".format(self.path, self.key, self.type, self.frequency)

    def __repr__(self):
        return str(self)

    def __key(self):
        return self.path

    def __eq__(self, other):
        return type(self) == type(other) and self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def is_hidden(self):
        return self.name.startswith('.')

    def is_plain_text_file(self):
        if self.__is_plain_text_file is None:
            self.__is_plain_text_file = self.is_file() and not is_binary(self.path)
        return self.__is_plain_text_file

    def is_dir(self) -> bool:
        return self.type == EntryType.DIRECTORY or self.is_link() and os.path.isdir(self.realpath)

    def is_file(self) -> bool:
        return self.type == EntryType.FILE or self.is_link() and os.path.islink(self.realpath)

    def is_link(self) -> bool:
        return self.type == EntryType.SYMLINK


def detect_type(mode) -> EntryType:
    if stat.S_ISREG(mode):
        return EntryType(EntryType.FILE)
    if stat.S_ISDIR(mode):
        return EntryType(EntryType.DIRECTORY)
    if stat.S_ISLNK(mode):
        return EntryType(EntryType.SYMLINK)
    if stat.S_ISFIFO(mode):
        return EntryType(EntryType.FIFO)
    if stat.S_ISBLK(mode):
        return EntryType(EntryType.BLOCK_DEVICE)
    if stat.S_ISCHR(mode):
        return EntryType(EntryType.CHARACTER_DEVICE)
