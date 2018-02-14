# defines the entry class which represents a file or directiory
import key
import os

if os.name == 'nt':
    pass
from mylogger import logger
from binaryornot.check import is_binary


class Entry:

    # path: the absolute, cannonical file path
    def __init__(self, path, issymlink=False):
        self.path = path
        self.dir, self.name = os.path.split(path)
        self.isdir = os.path.isdir(path)
        self.issymlink = issymlink
        self.key = key.Key("")
        self.frequency = 0
        # the children of this
        self.children = []
        self.__is_plain_text_file = None

    def __str__(self):
        return "[path:{}, key:{}, isdir:{}, frequency:{}]".format(self.path, self.key, self.isdir, self.frequency)

    def __repr__(self):
        return str(self)

    def __key(self):
        return (self.path)

    def __eq__(self, other):
        return (type(self) == type(other) and self.__key() == other.__key())

    def __hash__(self):
        return (hash(self.__key()))

    def is_hidden(self):
        if os.name == "nt":
            # TODO implement hidden file detection for windows. may never happen
            raise Exception('Hidden file detection not implemented for windows')
        else:
            return self.name.startswith('.')

    def is_plain_text_file(self):
        if self.__is_plain_text_file is None:
            self.__is_plain_text_file = not self.isdir and not is_binary(self.path)
        return self.__is_plain_text_file


def sort(entries):
    entryList = list(entries)
    entryList.sort(key=lambda x: x.name)
    entryList.sort(key=lambda x: x.isdir, reverse=True)
    entryList.sort(key=lambda x: x.is_hidden())
    entryList.sort(key=lambda x: x.key.value == "")
    entryList.sort(key=lambda x: x.frequency, reverse=True)
    return entryList
