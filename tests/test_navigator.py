import os
import shutil
from typing import Dict, List

from core import entry as entry_module
from core.dirhistory import DirHistory
from core.entry import Entry
from core.entryaccess import EntryAccess
from core.key import Key
from core.navigator import Navigator
from util import environment

test_dir = os.path.join(os.getcwd(), "tmp_data")

# tweak these numbers for benchmarking
# resulting count of files: intermediate_count * file_count
intermediate_count = 10
file_count = 10
top_level_entry: Entry = None
intermediate_entries: Dict[Key, Entry] = {}
file_entries: List[Dict[Key, Entry]] = []


def test_assign_key_conflict_swap():
    """When assigning a key to an entry and the key is already assigned to another entry, keys are swapped"""
    # entry = navigator.visit_path(test_dir)
    # entry.get_child(key)
    key = Key('a')
    other_key = Key('b')
    navigator.assign_key(key.value, intermediate_entries[other_key].path)


def setup_test_data():
    global top_level_entry
    global intermediate_entries
    global file_entries
    os.mkdir(test_dir)
    top_level_entry = entry_module.Entry(test_dir, key=Key('a'), frequency=5)
    for i in range(intermediate_count):
        files = {}
        child = os.path.join(test_dir, str(i))
        os.mkdir(child)
        key = Key(chr(97 + (i % 26)))
        entry = entry_module.Entry(child, key=key, frequency=i)
        intermediate_entries[key] = entry
        for j in range(file_count):
            grand_child = os.path.join(child, str(j))
            open(grand_child, 'a').close()
            key = Key(chr(97 + (j % 26)))
            entry = entry_module.Entry(grand_child, key=key, frequency=j)
            files[key] = entry
        file_entries.append(files)
    pass


@pytest.yield_fixture(autouse=True)
def fixture():
    global navigator
    try:
        shutil.rmtree(test_dir)
    except FileNotFoundError:
        pass
    setup_test_data()
    environment.db_path = os.path.join(test_dir, "tmp_db.sqlite")
    navigator = Navigator(DirHistory(), EntryAccess(EntryDao()))
    yield
    shutil.rmtree(test_dir)
