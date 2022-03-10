import functools
import os
from io import UnsupportedOperation
from pathlib import Path
from typing import Optional

from sodalite.core import rating, config
from sodalite.core.hook import Hook
from sodalite.core.key import Key


class Entry:
    """
    defines the entry class which represents a file or directory
    """

    def __init__(self, path: Path, access_history: list[int] = None, parent: 'Entry' = None, key: Key = Key('')):
        """
        :param path: the absolute, canonical path of this entry
        """
        self.path = Path(os.path.normpath(str(path)))
        self.unexplored = False
        self.access_history: list[int] = access_history or []
        self._rating: Optional[float] = None
        self.parent = parent
        self.dir: Path = self.path.parent
        self.name = path.name
        self._key = key

        self._children: list['Entry'] = []
        self.path_to_child: dict[Path, Entry] = {}
        self.key_to_child: dict[Key, Entry] = {}

        self.hooks: list[Hook] = []
        self.stat = os.lstat(path)
        self.size = self.stat.st_size
        self.permissions = oct(self.stat.st_mode)[-3:]

    @functools.cached_property
    def realpath(self) -> Path:
        if self.is_link:
            return self.path.resolve(strict=False)
        else:
            return self.path

    def chdir(self) -> None:
        """
        Change current (os) directory to this entry. If this entry is not a directory, changes to the parent directory.
        """
        if self.is_dir:
            cwd = self.realpath
        else:
            cwd = self.realpath.parent
        os.chdir(cwd)

    @property
    def children(self) -> list['Entry']:
        return self._children

    @children.setter
    def children(self, children: list['Entry']) -> None:
        self._children = children
        self.path_to_child.clear()
        self.key_to_child.clear()
        for entry in children:
            self.path_to_child[entry.path] = entry
            self.key_to_child[entry.key] = entry

    @property
    def key(self) -> Key:
        return self._key

    @key.setter
    def key(self, key: Key) -> None:
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

    @functools.cached_property
    def name_precedence(self) -> int:
        """lower precedence number means higher priority, e.g. for displaying"""
        try:
            return config.get().preferred_names.index(self.name.lower())
        except ValueError:
            return len(config.get().preferred_names)

    def __str__(self) -> str:
        return f"[path:{self.path}, key:{self.key}]"

    def __repr__(self) -> str:
        return str(self)

    def __key(self) -> str:
        return str(self.path)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Entry) and self.__key() == other.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    @property
    def is_hidden(self) -> bool:
        return self.name.startswith('.')

    @functools.cached_property
    def is_plain_text_file(self) -> bool:
        if self.is_file:
            from binaryornot import check
            return not self.name.endswith('.pdf') and not check.is_binary(str(self.path))
        else:
            return False

    @functools.cached_property
    def is_dir(self) -> bool:
        return self.path.is_dir()

    @functools.cached_property
    def is_file(self) -> bool:
        return self.path.is_file()

    @property
    def is_link(self) -> bool:
        return self.path.is_symlink()

    @property
    def exists(self) -> bool:
        return self.path.exists()

    # TODO use cache_property here
    @property
    def rating(self) -> float:
        if not isinstance(self._rating, float):
            if not self.parent:
                raise ValueError("Trying to get rating of entry which parent is not set")
            rating.populate_ratings(self.parent.children)
        assert self._rating is not None
        return self._rating

    @rating.setter
    def rating(self, rating: float) -> None:
        self._rating = rating

    @functools.cached_property
    def executable(self) -> bool:
        if self.is_link:
            return os.access(self.realpath, os.X_OK)
        else:
            owner = self.permissions[0]
            return owner == '1' or owner == '5' or owner == '7'

    @functools.cached_property
    def readable(self) -> bool:
        owner = int(self.permissions[0])
        return owner >= 4

    @functools.cached_property
    def content(self) -> str:
        if not self.is_plain_text_file:
            raise UnsupportedOperation
        return self.path.read_text()
