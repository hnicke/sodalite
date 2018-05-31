from random import shuffle
from typing import List

all_keys: List[List[str]] = []
all_keys.append(['a', 's', 'd', 'f', 'j', 'k', 'l'])
all_keys.append(['g', 'h', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'z', 'x', 'c', 'v', 'b', 'n', 'm'])
all_keys.append([x.upper() for x in all_keys[0]])
all_keys.append([x.upper() for x in all_keys[1]])


class Key:
    """all keys, divided into 4 groups:
    the first group is the group of keys which is intended to be assigned first, the last one last.
    """

    def compute_key_rank(self):
        """"# returns integer 1-4, depending on the key rank. the lower, the better.
        """
        self.rank = 4
        for x in range(3):
            if self.value in all_keys[x]:
                self.rank = x
                break

    def __init__(self, value):
        self.value = value
        self.rank = None
        self.compute_key_rank()

    def __str__(self):
        return self.value

    def __key(self):
        return self.value

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.rank > other.rank

    def __repr__(self):
        return str(self)


def get_all_keys():
    keys = []
    for rank in all_keys:
        shuffle(rank)
        keys.extend(rank)
    return keys


def get_available_keys(old_entries: dict) -> List[str]:
    """returns a list of keys which are not yet used by given entries
    :param old_entries: list of Entry which already have a key"""
    used_keys = set(map(lambda x: x.key.value, old_entries.values()))
    used_keys.discard('')
    unused_keys = []
    for i in range(4):
        tmp = list(set(all_keys[i]) - used_keys)
        shuffle(tmp)
        unused_keys.extend(tmp)
    return unused_keys


def assign_keys(new_entries: dict, old_entries: dict):
    """ assigns keys to the given new entries. Needs old entries
    :param new_entries: entries without key, these will receive a key
    :param old_entries: all entries of this domain which already have a key"""
    free_keys = get_available_keys(old_entries)
    sorted_new_entries = _sort(new_entries.values())
    entries_assign_later = []
    for entry in sorted_new_entries:
        if len(free_keys) > 0:
            # try to assign starting character as key
            start_char = entry.name[0].lower()
            if start_char in free_keys:
                free_keys.remove(start_char)
                char = start_char
            elif start_char.upper() in free_keys:
                free_keys.remove(start_char.upper())
                char = start_char.upper()
            else:
                entries_assign_later.append(entry)
                continue
            entry.key = Key(char)
        else:
            return
    # now assign keys for entries whose starting chars were already taken
    for entry in entries_assign_later:
        if len(free_keys) > 0:
            char = free_keys.pop(0)
            entry.key = Key(char)
        else:
            return


def is_navigation_key(key: str):
    for key_rank in all_keys:
        if key in key_rank:
            return True
    return False


def _sort(entries):
    sorted_entries = sorted(entries, key=lambda x: x.name)
    sorted_entries.sort(key=lambda x: x.is_dir(), reverse=True)
    sorted_entries.sort(key=lambda x: x.is_hidden())
    return sorted_entries
