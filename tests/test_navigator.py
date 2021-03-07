import os
import shutil
from pathlib import Path
from typing import Optional

import pytest

from sodalite.core import entry as entry_module
from sodalite.core.history import History
from sodalite.core.entry import Entry
from sodalite.core.entryaccess import EntryAccess
from sodalite.core.key import Key
from sodalite.core.navigate import Navigator
from sodalite.util import env

test_dir = Path.cwd() / "tmp_data"

# tweak these numbers for benchmarking
# resulting count of files: intermediate_count * file_count
intermediate_count = 10
file_count = 10
top_level_entry: Optional[Entry] = None
intermediate_entries: dict[Key, Entry] = {}
file_entries: list[dict[Key, Entry]] = []


def test_assign_key_conflict_swap():
    """When assigning a key to an entry and the key is already assigned to another entry, keys are swapped"""
    pytest.skip('needs refactoring')
    # entry = navigator.visit_path(test_dir)
    # entry.get_child(key)
    key = Key('a')
    other_key = Key('b')
    navigator.assign_key(key.value, intermediate_entries[other_key].path)


def setup_test_data():
    pytest.skip('needs refactoring')
    global top_level_entry
    global intermediate_entries
    global file_entries
    test_dir.mkdir()
    top_level_entry = entry_module.Entry(str(test_dir.absolute()), key=Key('a'))
    for i in range(intermediate_count):
        files = {}
        child = os.path.join(test_dir, str(i))
        os.mkdir(child)
        key = Key(chr(97 + (i % 26)))
        entry = entry_module.Entry(child, key=key)
        intermediate_entries[key] = entry
        for j in range(file_count):
            grand_child = os.path.join(child, str(j))
            open(grand_child, 'a').close()
            key = Key(chr(97 + (j % 26)))
            entry = entry_module.Entry(grand_child, key=key)
            files[key] = entry
        file_entries.append(files)
    pass


@pytest.fixture(autouse=True)
def fixture():
    pytest.skip('needs refactoring')
    global navigator
    shutil.rmtree(test_dir, ignore_errors=True)
    setup_test_data()
    env.db_file = test_dir / "tmp_db.sqlite"
    navigator = Navigator(History([str(test_dir)]), EntryAccess())
    yield
    shutil.rmtree(test_dir)
