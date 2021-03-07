import logging
import re
import sqlite3
from typing import Dict, Iterable, List

from sodalite.core import key as key_module
from sodalite.core.entry import Entry
from sodalite.core.key import Key
from sodalite.core.operate import Operation
from sodalite.util import environment

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

TABLE_OPERATION = 'operation'
OPERATION_TIMESTAMP = 'timestamp'
OPERATION_ACTION = 'action'
OPERATION_PARAMS = 'params'

CREATE_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_ENTRY} (
    {ENTRY_PATH} TEXT PRIMARY KEY,
    {ENTRY_KEY} TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS {TABLE_ACCESS} (
    {ACCESS_PATH} TEXT,
    {ACCESS_TIMESTAMP} INTEGER,
    CONSTRAINT fk_entry
        FOREIGN KEY({ACCESS_PATH})
        REFERENCES {TABLE_ENTRY}({ENTRY_PATH})
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS {TABLE_OPERATION} (
    {OPERATION_TIMESTAMP} INTEGER PRIMARY KEY, 
    {OPERATION_ACTION} TEXT NOT NULL,
    {OPERATION_PARAMS} TEXT NOT NULL
);"""


class DbEntry:
    def __init__(self, path: str, key: Key = None, access_history: List[int] = None):
        if not key:
            key = Key('')
        if not access_history:
            access_history = []
        self.path: str = path
        self.key: Key = key
        self.access_history: List[int] = access_history

    def to_entry(self, parent: Entry) -> Entry:
        return Entry(path=self.path, key=self.key, access_history=self.access_history, parent=parent)


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def open_connection():
    conn = sqlite3.connect(environment.db_file)
    conn.create_function("REGEXP", 2, regexp)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init():
    conn = open_connection()
    conn.cursor().executescript(CREATE_SCHEMA)
    conn.close()


# TODO refactor: use decorators for opening / closing the db connection

init()


def inject_data(entry: Entry):
    """
    Injects key and frequency information into children of given entry
    """
    entries_fs: Dict[str, Entry] = entry.path_to_child
    entries_db: Dict[str, DbEntry] = get_children(entry.realpath)
    # remove obsolete entries
    obsolete_paths = entries_db.keys() - entries_fs.keys()
    remove_entries(obsolete_paths)
    entries_db = {path: entry_db for (path, entry_db) in entries_db.items() if path not in obsolete_paths}
    # inject values
    old_entries = {}
    for db_entry in entries_db.values():
        child = entry.get_child_for_path(db_entry.path)
        if child:
            child.key = db_entry.key
            child.access_history = db_entry.access_history
            old_entries[child.path] = child
    insert_new_entries(entries_fs, old_entries)


def get_children(path: str) -> Dict[str, DbEntry]:
    """
    Queries the database for all child entries belonging to given entry
    """
    # fix regex for root
    if path == '/':
        path = ''
    query = f"^{path}/[^/]+$"
    return read_entries_from_db(query)


def read_entries_from_db(regex: str) -> Dict[str, DbEntry]:
    """
    :param regex:
    :return: Dict: path -> (key, frequency)
    """
    query = f"""
    SELECT {TABLE_ENTRY}.{ENTRY_PATH}, {TABLE_ENTRY}.{ENTRY_KEY}, {TABLE_ACCESS}.{ACCESS_TIMESTAMP}
    FROM {TABLE_ENTRY} 
    LEFT JOIN {TABLE_ACCESS} ON {TABLE_ENTRY}.{ENTRY_PATH}={TABLE_ACCESS}.{ACCESS_PATH}
    WHERE {TABLE_ENTRY}.{ENTRY_PATH} REGEXP ?
    """
    conn = open_connection()
    try:
        cursor = conn.cursor().execute(query, (regex,))
        result: Dict[str, DbEntry] = {}
        for row in cursor:
            path = row[0]
            access = row[2]
            if access is not None and path in result:
                result[path].access_history.append(access)

            else:
                key = Key(row[1])
                access_history = []
                if access is not None:
                    access_history.append(access)
                entry = DbEntry(path, key=key, access_history=access_history)
                result[path] = entry
        return result
    finally:
        conn.close()


def insert_new_entries(entries_fs: Dict[str, Entry], entries_db: Dict[str, Entry]):
    new_paths = entries_fs.keys() - entries_db.keys()
    if not new_paths:
        return
    new_entries = {path: entries_fs[path] for path in new_paths}
    for path in new_paths:
        logger.info("Persisting new entry: {}".format(path))
    reassigned_old_entries = key_module.assign_keys(new_entries, entries_db)
    for entry in reassigned_old_entries:
        update_entry(entry)
    query = f"INSERT INTO {TABLE_ENTRY} VALUES "
    parameters = []
    for entry in new_entries.values():
        query += "(?,?),"
        parameters += [entry.path, entry.key.value]
    query = query[:-1] + ';'
    conn = open_connection()
    try:
        conn.cursor().execute(query, (*parameters,))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.error("Integrity error. failed to insert at least one of " + str(new_paths))
    finally:
        conn.close()


def entry_exists(path: str) -> bool:
    query = f"""SELECT EXISTS (SELECT 1 FROM {TABLE_ENTRY} WHERE ({ENTRY_PATH}) = ?)"""
    conn = open_connection()
    try:
        exists = conn.cursor().execute(query, (path,)).fetchone()[0]
        return exists
    finally:
        conn.close()


def insert_entry(entry):
    query = f"""INSERT INTO {TABLE_ENTRY} ({ENTRY_PATH},{ENTRY_KEY}) VALUES (?,?)"""
    conn = open_connection()
    try:
        conn.cursor().execute(query, (entry.path, entry.key.value))
        conn.commit()
    finally:
        conn.close()


def remove_entries(obsolete_paths: Iterable[str]):
    """Deletes obsolete entries in the db"""
    if not obsolete_paths:
        return
    query = f"DELETE FROM {TABLE_ENTRY} WHERE {ENTRY_PATH} REGEXP ?"
    conn = open_connection()
    try:
        regex = '^('
        for path in obsolete_paths:
            regex += re.escape(path) + '(/.*)*|'
        regex = regex[:-1] + ')$'
        conn.cursor().execute(query, (regex,))
        conn.commit()
    finally:
        conn.close()


def update_entry(entry: Entry):
    """Updates given entry in database"""
    query = f"UPDATE {TABLE_ENTRY} SET {ENTRY_KEY}=? WHERE {ENTRY_PATH}=?"
    conn = open_connection()
    try:
        conn.cursor().execute(query, (entry.key.value, entry.path))
        conn.commit()
    finally:
        conn.close()


def rename_entry(entry: Entry, new_name: str):
    # old_path = entry.path
    # new_path = os.path.join(entry.dir, new_name)
    # query = f"""-- SELECT {ENTRY_PATH},{ENTRY_KEY} FROM {TABLE_ENTRY} WHERE {ENTRY_PATH} REGEXP ?"""
    # regex = f"^{re.escape(old_path)}(/.*)*$"
    # conn = open_connection()
    # try:
    #     cursor = conn.cursor().execute(query, (regex,))
    #     paths_to_rename = [row[0] for row in cursor]
    #     new_paths = [x.replace(old_path, new_path, 1) for x in paths_to_rename]
    #     update_entries = f"""UPDATE {TABLE_ENTRY} WHERE """
    #     pass
    # finally:
    #     conn.close()
    pass


def insert_access(path: str, access: int):
    query = f"INSERT INTO {TABLE_ACCESS} VALUES (?,?)"
    conn = open_connection()
    try:
        conn.cursor().execute(query, (path, access))
        conn.commit()
    finally:
        conn.close()


def get_operations():
    query = f"""SELECT ({OPERATION_ACTION},{OPERATION_PARAMS},{OPERATION_TIMESTAMP})
            FROM {TABLE_OPERATION} SORT BY {OPERATION_TIMESTAMP} ASC"""
    conn = open_connection()
    try:
        cursor = conn.cursor().execute(query)
        # TODO module core now depends on ui. operation should go to core?
        return [Operation(row[0], params=eval(row[1]), timestamp=[2]) for row in cursor]
    finally:
        conn.close()


def insert_operation(operation: Operation):
    query = f"""INSERT INTO {TABLE_OPERATION} ({OPERATION_ACTION},{OPERATION_PARAMS},{OPERATION_TIMESTAMP})
    VALUES (?,?,?)"""
    conn = open_connection()
    try:
        conn.cursor().execute(query, (operation.action_name, str(operation.params), operation.timestamp))
        conn.commit()
    finally:
        conn.close()


def delete_operation(operation: Operation):
    query = f"DELETE FROM {TABLE_OPERATION} WHERE {OPERATION_TIMESTAMP} = ?"
    conn = open_connection()
    try:
        conn.cursor().execute(query, (operation.timestamp,))
        conn.commit()
    finally:
        conn.close()
