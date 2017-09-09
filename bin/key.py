#key.py

# handles all logic around key handling

import string
from random import shuffle 
import entry as entry_module
from mylogger import logger

all_keys = []
all_keys.append([ 'a', 's', 'd', 'f', 'j', 'k', 'l' ])
all_keys.append([ 'g', 'h', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'z', 'x', 'c', 'v', 'b', 'n', 'm' ])
all_keys.append([ x.upper() for x in all_keys[0]])
all_keys.append([ x.upper() for x in all_keys[1]])

class Key:
    # all keys, divided into 4 groups: the first group is the group of keys which is intended to be assigned first, the last one last.

# returns integer 1-4, depending on the key rank. the lower, the better
    def compute_key_rank( self ):
        self.rank=4
        for x in range( 3 ):
            if self.value in all_keys[x]:
                self.rank=x
                break

    def __init__( self, value ):
        self.value = value
        self.rank = None
        self.compute_key_rank()

    def __str__( self ):
        return self.value

    def __key( self ):
        return ( self.value)

    def __eq__( self, other ):
        return ( self.__key() == other.__key())

    def __hash__( self ):
        return (hash(self.__key()))

    def __lt__( self, other ):
        return self.rank > other.rank

    def __repr__( self ):
        return str(self)



def get_all_keys():
    keys = []
    for rank in all_keys:
        shuffle(rank)
        keys.extend( rank )
    return keys



# returns a list of keys which are not yet used by given entries
# old_entries: list of Entry which alreay have a key
def get_available_keys( old_entries ):
    used_keys = map(lambda x: x.key.value, old_entries)
    unused_keys = []
    for i in range( 3 ):
        tmp = list(set(all_keys[i]) - set(used_keys))
        shuffle(tmp)
        unused_keys.extend(tmp)
    return unused_keys

# assigns keys to the given new entries
# new_entries: entries without key, these will receive a key
# old_entires: all entries of this domain which already have a key
def assign_keys( new_entries, old_entries ):
    unused_keys = get_available_keys( old_entries)
    entry_module.sort(new_entries)
    for entry in new_entries:
        if len(unused_keys) > 0:
            entry.key = Key(unused_keys.pop(0))
        else:
            # TODO
            # what shall we do if we dont have enough keys?
            break
    return
