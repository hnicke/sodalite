from random import shuffle
from typing import List

all_keys: List[List[str]] = []
all_keys.append(['a', 's', 'd', 'f', 'j', 'k', 'l'])
all_keys.append(['g', 'h', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'z', 'x', 'c', 'v', 'b', 'n', 'm'])
all_keys.append([x.upper() for x in all_keys[0]])
all_keys.append([x.upper() for x in all_keys[1]])
all_keys.append([str(x) for x in range(10)])


class Key:
    """all keys, divided into 5 groups:
    the first group is the group of keys which is intended to be assigned first, the last one last.
    """

    def compute_key_rank(self):
        """"# returns integer 1-5, depending on the key rank. the lower, the better.
        """
        self.rank = len(all_keys)
        for x in range(len(all_keys) - 1):
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


def _get_available_keys(old_entries: dict) -> List[str]:
    """returns a list of keys which are not yet used by given entries
    :param old_entries: list of Entry which already have a key"""
    used_keys = set(map(lambda x: x.key.value, old_entries.values()))
    used_keys.discard('')
    unused_keys = []
    for key_rank in all_keys:
        tmp = list(set(key_rank) - used_keys)
        shuffle(tmp)
        unused_keys.extend(tmp)
    return unused_keys


def assign_keys(entries_to_assign: dict, old_entries: dict):
    """ assigns keys to the given new entries. Needs old entries
    :param entries_to_assign: entries without key, these will receive a key
    :param old_entries: all entries of this domain which already have a key
    :return list of old entries whose keys got reassigned and therefore need to get persisted
    """

    if not entries_to_assign:
        return
    free_keys = _get_available_keys(old_entries)
    reassignable_keys = [x.key.value for x in old_entries.values() if x.rating < 0.05 and x.key.value != '']
    available_keys = free_keys + reassignable_keys
    sorted_new_entries = _sort(entries_to_assign.values())
    _assign(sorted_new_entries, available_keys)

    # now try reassign keys to these entries who just lost their key
    reassigned_keys = [x for x in reassignable_keys if x not in available_keys]
    entries_to_reassign = [x for x in old_entries.values() if x.key.value in reassigned_keys]
    for entry in entries_to_reassign:
        entry.key = Key('')
    _assign(entries_to_reassign,
            [x for x in free_keys if x not in available_keys])
    return entries_to_reassign


def _assign(entries: List, available_keys: List[str]):
    entries_assign_later = []
    for entry in entries:
        if len(available_keys) > 0:
            # try to assign starting character as key
            start_char = entry.name.lstrip('.')[0].lower()
            if start_char in available_keys:
                available_keys.remove(start_char)
                char = start_char
            elif start_char.upper() in available_keys:
                available_keys.remove(start_char.upper())
                char = start_char.upper()
            else:
                entries_assign_later.append(entry)
                continue
            entry.key = Key(char)
        else:
            return
    # now assign keys for entries whose starting chars were already taken
    for entry in entries_assign_later:
        if len(available_keys) > 0:
            char = available_keys.pop(0)
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
    sorted_entries.sort(key=lambda x: x.name_precedence)
    return sorted_entries
