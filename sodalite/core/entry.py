import os
import stat
from enum import Enum
from io import UnsupportedOperation
from pathlib import Path
from typing import Dict, Iterable, List

from binaryornot.check import is_binary

from core import rating
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

    def __init__(self, path: str, access_history: List[int] = None, parent: 'Entry' = None, key: Key = Key('')):
        """
        :param path: the absolute, canonical path of this entry
        """
        self.path = path
        if not access_history:
            access_history = []
        self.access_history: List[int] = access_history
        self._rating = None
        self._parent = parent
        self.dir, self.name = os.path.split(path)
        self._key = key

        self._children: List['Entry'] = []
        self.path_to_child: Dict[str, Entry] = {}
        self.key_to_child: Dict[Key, Entry] = {}

        self.__is_plain_text_file = None
        self.hooks: list = []
        self.stat = os.lstat(path)
        self.size = self.stat.st_size
        self.permissions = oct(self.stat.st_mode)[-3:]
        self.type = detect_type(self.stat.st_mode)
        if self.is_link():
            self.realpath = os.path.join(os.path.dirname(path), os.readlink(path))
        else:
            self.realpath = path
        self._executable = None
        self._readable = None
        self._content = None

    def chdir(self):
        """
        Change current (os) directory to this entry. If this entry is not a directory, changes to the parent directory.
        """
        if self.is_dir():
            cwd = self.realpath
        else:
            cwd = os.path.dirname(self.realpath)
        os.chdir(cwd)

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
            self.key_to_child[entry.key] = entry

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key: Key):
        if self._parent and self._key in self._parent.key_to_child:
            if self._parent.key_to_child[self._key] == self:
                del self._parent.key_to_child[self._key]
        self._key = key
        if self._parent:
            self._parent.key_to_child[key] = self

    def get_child_for_key(self, key: Key) -> 'Entry' or None:
        return self.key_to_child.get(key, None)

    def get_child_for_path(self, path: str) -> 'Entry' or None:
        return self.path_to_child.get(path, None)

    def __str__(self):
        return "[path:{}, key:{}, type:{}]".format(self.path, self.key, self.type)

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
            self.__is_plain_text_file = self.is_file() and not self.name.endswith('.pdf') and not is_binary(self.path)
        return self.__is_plain_text_file

    def is_dir(self) -> bool:
        return self.type == EntryType.DIRECTORY or self.is_link() and os.path.isdir(self.realpath)

    def is_file(self) -> bool:
        return self.type == EntryType.FILE or self.is_link() and os.path.isfile(self.realpath)

    def is_link(self) -> bool:
        return self.type == EntryType.SYMLINK

    def exists(self) -> bool:
        return Path(self.path).exists()

    @property
    def rating(self):
        if not self._rating:
            if not self._parent:
                raise ValueError("Trying to get rating of entry which parent is not set")
            rating.populate_ratings(self._parent.children)
        assert self._rating is not None
        return self._rating

    @rating.setter
    def rating(self, rating):
        self._rating = rating

    @property
    def executable(self) -> bool:
        if not self._executable:
            if self.is_link():
                self._executable = os.access(self.realpath, os.X_OK)
            else:
                owner = self.permissions[0]
                self._executable = owner == '1' or owner == '5' or owner == '7'
        return self._executable

    @property
    def readable(self):
        if not self._executable:
            owner = int(self.permissions[0])
            self._readable = owner >= 4
        return self._readable

    @property
    def content(self):
        if not self.is_plain_text_file():
            raise UnsupportedOperation
        if not self._content:
            with open(self.path) as f:
                self._content = f.read()
        return self._content


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
