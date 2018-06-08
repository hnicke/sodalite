import logging
import re
import sqlite3
from typing import Dict, Iterable

from core import key as key_module
from core.entry import Entry
from core.frecency import Access, AccessHistory
from core.key import Key
from util import environment

"""
Handles database access
"""

logger = logging.getLogger(__name__)

TABLE_ENTRY = 'entry'
ENTRY_PATH = 'path'
ENTRY_KEY = 'key'

TABLE_ACCESS = 'access'
ACCESS_PATH = 'path'
ACCESS_TIMESTAMP = 'timestamp'

CREATE_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_ENTRY} (
    {ENTRY_PATH} TEXT PRIMARY KEY,
    {ENTRY_KEY} TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS {TABLE_ACCESS} (
    {ACCESS_PATH} TEXT,
    {ACCESS_TIMESTAMP} INTEGER,
    CONSTRAINT fk_entry
        FOREIGN KEY({ACCESS_PATH})
        REFERENCES {TABLE_ENTRY}({ENTRY_PATH})
        ON DELETE CASCADE
);"""


class DbEntry:
    def __init__(self, path: str, key: Key, access_history):
        self.path = path
        self.key = key
        self.access_history = access_history


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def open_connection():
    conn = sqlite3.connect(environment.db_path)
    conn.create_function("REGEXP", 2, regexp)
    return conn


def init():
    conn = open_connection()
    conn.cursor().executescript(CREATE_SCHEMA)
    conn.close()


init()


def inject_data(entry):
    """
    Injects key and frequency information into children of given entry
    """
    entries_fs: Dict[str, Entry] = entry.path_to_child
    entries_db: Dict[str, DbEntry] = get_db_entries(entry)
    # remove obsolete entries
    obsolete_paths = entries_db.keys() - entries_fs.keys()
    remove_entries(obsolete_paths)
    entries_db = {path: entry_db for (path, entry_db) in entries_db.items() if path not in obsolete_paths}
    # inject values
    for db_entry in entries_db.values():
        child = entry.get_child_for_path(db_entry.path)
        child.key = db_entry.key
        child.frequency = db_entry.frequency
    insert_new_entries(entries_fs, entries_db)


def get_db_entries(parent: Entry) -> Dict[str, DbEntry]:
    """
    Queries the database for all child entries belonging to given entry
    """
    basedir = parent.realpath
    # fix regexp for root
    if basedir == '/':
        basedir = ''
    children = '{}/[^/]+$'.format(basedir)
    query = '^{}'.format(children)
    return read_entries_from_db(query)


def read_entries_from_db(regexp: str) -> Dict[str, DbEntry]:
    """
    :param regexp:
    :return: Dict: path -> (key, frequency)
    """
    query = f"""
    SELECT {TABLE_ENTRY}.{ENTRY_PATH}, {TABLE_ENTRY}.{ENTRY_KEY}, {TABLE_ACCESS}.{ACCESS_TIMESTAMP}
    FROM {TABLE_ENTRY} 
    LEFT JOIN {TABLE_ACCESS} ON {TABLE_ENTRY}.{ENTRY_PATH}={TABLE_ACCESS}.{ACCESS_PATH}
    WHERE {ENTRY_PATH} REGEXP ?
    """
    conn = open_connection()
    try:
        cursor = conn.cursor().execute(query, (regexp,))
        result = {}
        for row in cursor:
            path = row[0]
            access = Access(row[2])
            if path in result:
                result[path].access_history.append(access)
            else:
                key = Key(row[1])
                entry = DbEntry(path, key, AccessHistory([access]))
                result[path] = entry
        return result
    finally:
        conn.close()


def insert_new_entries(entries_fs: Dict[str, Entry], entries_db: Dict[str, DbEntry]):
    new_paths = entries_fs.keys() - entries_db.keys()
    if not new_paths:
        return
    new_entries = {path: entries_fs[path] for path in new_paths}
    for path in new_paths:
        logger.info("Persisting new entry: {}".format(path))
    key_module.assign_keys(new_entries, entries_db)
    query = f"INSERT INTO {TABLE_ENTRY} VALUES "
    for entry in new_entries.values():
        query += "('{}','{}','{}'),".format(entry.path, entry.key.value, entry.frequency)
    query = query[:-1] + ';'
    conn = open_connection()
    try:
        conn.cursor().execute(query)
        conn.commit()
    except sqlite3.IntegrityError:
        logger.error("Integrity error. failed to insert at least one of " + str(new_paths))
    finally:
        conn.close()


def remove_entries(obsolete_paths: Iterable[str]):
    """Deletes obsolete entries in the db"""
    query = f"DELETE FROM {TABLE_ENTRY} WHERE {ENTRY_PATH} REGEXP ?"
    conn = open_connection()
    try:
        for path in obsolete_paths:
            regexp = '^' + path + '(/.*)*$'
            conn.cursor().execute(query, (regexp,))
        conn.commit()
    finally:
        conn.close()


def update_entry(entry):
    """Updates given entry in database"""
    query = f"UPDATE {TABLE_ENTRY} SET {ENTRY_KEY}=? WHERE {ENTRY_PATH}=?"
    conn = open_connection()
    try:
        conn.cursor().execute(query, (entry.key.value, entry.path))
        conn.commit()
    finally:
        conn.close()


def insert_access(path: str, access: Access):
    query = f"INSERT INTO {TABLE_ACCESS} VALUES ({path},{access.timestamp})"
    conn = open_connection()
    try:
        conn.cursor().execute(query, (path, access.timestamp))
    finally:
        conn.close()
