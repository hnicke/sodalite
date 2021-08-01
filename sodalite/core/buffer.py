import logging
import os
import shutil
from pathlib import Path
from typing import Union

from sodalite.core.entry import Entry
from sodalite.util import env

logger = logging.getLogger(__name__)


class Register:
    def __init__(self, number: int):
        self.name = f"register{number}"
        self._path = env.buffer / self.name

    def copy_to(self, src: Union[list[Entry], Entry]) -> None:
        """
        Writes given entries or given entry to this register
        """

        def write_single_entry(e: Entry) -> None:
            logger.info(f"Yanking {e.name} to {self.name}")
            copy(e.path, self.path / e.name)

        self.clear()
        if isinstance(src, list):
            for entry in src:
                write_single_entry(entry)
        else:
            write_single_entry(src)

    def move_to(self, entry: Entry) -> None:
        self.clear()
        dest = self.path / entry.name
        logger.info(f"Moving {entry.path} to {dest}")
        shutil.move(entry.path, dest)

    def read_from(self, target: Entry) -> None:
        """
        Copies this registers content into given target dir
        """
        for file in self.path.iterdir():
            src = self.path / file
            dest = target.path / file
            logger.info(f"Pasting {self.name} to {dest}")
            copy(src, dest)

    def clear(self) -> None:
        for file in os.listdir(self.path):
            path = os.path.join(self.path, file)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    @property
    def path(self) -> Path:
        os.makedirs(self._path, exist_ok=True)
        return self._path


registers = [Register(x) for x in range(10)]


def copy(src: Path, dest: Path) -> None:
    """
    Recursively copy src to dest
    :param src:
    :param dest:
    :return:
    """
    try:
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)
    except OSError as e:
        logger.error(f"Failed to yank dir. Error: {e}")
