import os
import stat
from enum import Enum
from io import UnsupportedOperation
from numbers import Number
from pathlib import Path
from typing import Optional

from binaryornot.check import is_binary

from sodalite.core import rating, config
from sodalite.core.hook import Hook
from sodalite.core.key import Key


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

    def __init__(self, path: Path, access_history: list[int] = None, parent: 'Entry' = None, key: Key = Key('')):
        """
        :param path: the absolute, canonical path of this entry
        """
        self.path = Path(os.path.normpath(str(path)))
        if not access_history:
            access_history = []
        self.unexplored = False
        self.access_history: list[int] = access_history
        self._rating: Optional[float] = None
        self.parent = parent
        self.dir: Path = self.path.parent
        self.name = path.name
        self._key = key

        self._children: list['Entry'] = []
        self.path_to_child: dict[Path, Entry] = {}
        self.key_to_child: dict[Key, Entry] = {}

        self.__is_plain_text_file: Optional[bool] = None
        self.hooks: list[Hook] = []
        self.stat = os.lstat(path)
        self.size = self.stat.st_size
        self.permissions = oct(self.stat.st_mode)[-3:]
        self.type = detect_type(self.stat.st_mode)
        if self.is_link():
            self.realpath = self.path.resolve(strict=False)
        else:
            self.realpath = path
        """lower precedence number means higher priority, e.g. for displaying"""
        self.name_precedence = compute_name_precedence(self.name)
        self._executable: Optional[bool] = None
        self._readable = None
        self._content: Optional[str] = None

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
    def children(self, children: list['Entry']):
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
        if self.parent and self._key in self.parent.key_to_child:
            if self.parent.key_to_child[self._key] == self:
                del self.parent.key_to_child[self._key]
        self._key = key
        if self.parent:
            self.parent.key_to_child[key] = self

    def get_child_for_key(self, key: Key) -> Optional['Entry']:
        return self.key_to_child.get(key, None)

    def get_child_for_path(self, path: Path) -> Optional['Entry']:
        return self.path_to_child.get(path, None)

    def __str__(self) -> str:
        return "[path:{}, key:{}, type:{}]".format(self.path, self.key, self.type)

    def __repr__(self) -> str:
        return str(self)

    def __key(self) -> str:
        return str(self.path)

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.__key() == other.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    def is_hidden(self) -> bool:
        return self.name.startswith('.')

    def is_plain_text_file(self) -> bool:
        if self.__is_plain_text_file is None:
            self.__is_plain_text_file = self.is_file() \
                                        and not self.name.endswith('.pdf') and not is_binary(str(self.path))
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
        if not isinstance(self._rating, Number):
            if not self.parent:
                raise ValueError("Trying to get rating of entry which parent is not set")
            rating.populate_ratings(self.parent.children)
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
    elif stat.S_ISDIR(mode):
        return EntryType(EntryType.DIRECTORY)
    elif stat.S_ISLNK(mode):
        return EntryType(EntryType.SYMLINK)
    elif stat.S_ISFIFO(mode):
        return EntryType(EntryType.FIFO)
    elif stat.S_ISBLK(mode):
        return EntryType(EntryType.BLOCK_DEVICE)
    elif stat.S_ISCHR(mode):
        return EntryType(EntryType.CHARACTER_DEVICE)
    else:
        raise Exception(f"Unknown entry type '{mode}'")


def compute_name_precedence(name: str) -> int:
    try:
        return config.get().preferred_names.index(name.lower())
    except ValueError:
        return len(config.get().preferred_names)
