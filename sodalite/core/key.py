from pathlib import Path
from random import shuffle
from typing import TYPE_CHECKING, Collection, Iterable

if TYPE_CHECKING:
    from sodalite.core.entry import Entry

all_keys: list[list[str]] = []
all_keys.append(['a', 's', 'd', 'f', 'j', 'k', 'l'])
all_keys.append(['g', 'h', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'z', 'x', 'c', 'v', 'b', 'n', 'm'])
all_keys.append([x.upper() for x in all_keys[0]])
all_keys.append([x.upper() for x in all_keys[1]])
all_keys.append([str(x) for x in range(10)])


class Key:
    """all keys, divided into 5 groups:
    the first group is the group of keys which is intended to be assigned first, the last one last.
    """

    def __init__(self, value: str = '') -> None:
        self.value = value
        self.rank = self._compute_rank()

    def _compute_rank(self) -> int:
        """# returns integer 1-5, depending on the key rank. the lower, the better."""
        for x in range(len(all_keys) - 1):
            if self.value in all_keys[x]:
                return x
        return len(all_keys)

    def __str__(self) -> str:
        return self.value

    def __key(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.__key() == other.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    def __lt__(self, other: 'Key') -> bool:
        return self.rank > other.rank

    def __repr__(self) -> str:
        return str(self)


def get_all_keys() -> list[str]:
    keys = []
    for rank in all_keys:
        shuffle(rank)
        keys.extend(rank)
    return keys


def _get_available_keys(entries: Iterable['Entry']) -> list[str]:
    """returns a list of keys which are not yet used by given entries
    :param entries: entries which already have a key"""
    used_keys = set([x.key.value for x in entries])
    used_keys.discard('')
    unused_keys = []
    for key_rank in all_keys:
        tmp = list(set(key_rank) - used_keys)
        shuffle(tmp)
        unused_keys.extend(tmp)
    return unused_keys


def assign_keys(entries_to_assign: dict[Path, 'Entry'], old_entries: dict[Path, 'Entry']) -> list['Entry']:
    """
    assigns keys to the given new entries.
    Needs old entries to work properly.
    Existing entries with a very low rating can lose their key to a new entry.

    :param entries_to_assign: entries without key, these will receive a key
    :param old_entries: all entries of this domain which already have a key
    :return list of old entries whose keys got reassigned and therefore need to get persisted
    """

    free_keys = _get_available_keys(old_entries.values())
    reassignable_keys = [x.key.value for x in old_entries.values() if x.rating < 0.05 and x.key.value != '']
    available_keys = free_keys + reassignable_keys
    sorted_new_entries = _sort(entries_to_assign.values())
    _assign(sorted_new_entries, available_keys)

    # now try reassign keys to these entries which just lost their key
    all_entries = set(old_entries.values()).union(sorted_new_entries)
    free_keys = _get_available_keys(all_entries)
    reassigned_keys = [x for x in reassignable_keys if x not in available_keys]
    entries_to_reassign = [x for x in old_entries.values() if x.key.value in reassigned_keys]
    for entry in entries_to_reassign:
        entry.key = Key()
    _assign(entries_to_reassign, free_keys)
    return entries_to_reassign


def _assign(entries: list['Entry'], available_keys: list[str]) -> None:
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


def is_navigation_key(key: str) -> bool:
    for key_rank in all_keys:
        if key in key_rank:
            return True
    return False


def _sort(entries: Collection['Entry']) -> list['Entry']:
    sorted_entries = sorted(entries, key=lambda x: x.name)
    sorted_entries.sort(key=lambda x: x.is_dir, reverse=True)
    sorted_entries.sort(key=lambda x: x.is_hidden)
    sorted_entries.sort(key=lambda x: x.name_precedence)
    return sorted_entries
