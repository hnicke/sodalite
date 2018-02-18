import re
import sqlite3
from typing import Dict, Iterable

import atexit

import environment
from core import key as key_module
from core.entry import Entry
from core.key import Key
from mylogger import logger

TABLE_FILES = 'files'
COLUMN_PATH = 'path'
COLUMN_KEY = 'key'
COLUMN_FREQUENCY = 'frequency'

CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TABLE_FILES} (
    {COLUMN_PATH} text NOT NULL,
    {COLUMN_KEY} text NOT NULL,
    {COLUMN_FREQUENCY} INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY ( {COLUMN_PATH} )
)"""


class EntryDao:
    class DbEntry:
        def __init__(self, path: str, key: Key, frequency: int):
            self.path = path
            self.key = key
            self.frequency = frequency

    def __init__(self):
        """
        Handles database access
        """
        self.conn = sqlite3.connect(environment.db_path)
        atexit.register(self.conn.close)
        self.conn.create_function("REGEXP", 2, regexp)
        self.conn.cursor().execute(CREATE_TABLE)

    def inject_data(self, entry):
        """
        Injects key and frequency information into children of given entry
        """
        entries_fs: Dict[str, Entry] = entry.path_to_child
        entries_db: Dict[str, self.DbEntry] = self.get_db_entries(entry)
        # remove obsolete entries
        obsolete_paths = entries_db.keys() - entries_fs.keys()
        self.remove_entries(obsolete_paths)
        # inject values
        for db_entry in entries_db.values():
            child = entry.get_child_for_path(db_entry.path)
            child.key = db_entry.key
            child.frequency = db_entry.frequency
        self.insert_new_entries(entries_fs, entries_db)

    def get_db_entries(self, parent: Entry) -> Dict[str, DbEntry]:
        """
        Queries the database for all child entries belonging to given entry            atexit.register(self.close())
        """
        basedir = parent.realpath
        # fix regexp for root
        if basedir == '/':
            basedir = ''
        children = '{}/[^/]+$'.format(basedir)
        query = '^{}'.format(children)
        return self.read_entries_from_db(query)

    def read_entries_from_db(self, regexp: str) -> Dict[str, DbEntry]:
        """
        :param regexp:
        :return: Dict: path -> (key, frequency)
        """
        query = f"SELECT {COLUMN_PATH},{COLUMN_KEY},{COLUMN_FREQUENCY} FROM {TABLE_FILES} WHERE {COLUMN_PATH} REGEXP ?"
        cursor = self.conn.cursor().execute(query, (regexp,))
        result = {}
        for row in cursor:
            path = (row[0])
            key = Key(row[1])
            frequency = row[2]
            entry = self.DbEntry(path, key, frequency)
            result[path] = entry
        return result

    def insert_new_entries(self, entries_fs: Dict[str, Entry], entries_db: Dict[str, DbEntry]):
        new_paths = entries_fs.keys() - entries_db.keys()
        if not new_paths:
            return
        new_entries = {path: entries_fs[path] for path in new_paths}
        for path in new_paths:
            logger.info("Persisting new entry: {}".format(path))
        key_module.assign_keys(new_entries, entries_db)
        query = f"INSERT INTO {TABLE_FILES} VALUES "
        for entry in new_entries.values():
            query += "('{}','{}','{}'),".format(entry.path, entry.key.value, entry.frequency)
        query = query[:-1] + ';'
        try:
            self.conn.cursor().execute(query)
            self.conn.commit()
        except sqlite3.IntegrityError:
            logger.error("Integrity error. failed to insert at least one of " + str(new_paths))

    def remove_entries(self, obsolete_paths: Iterable[str]):
        """Deletes obsolete entries in the db"""
        query = f"DELETE FROM {TABLE_FILES} WHERE {COLUMN_PATH}=?"
        for path in obsolete_paths:
            self.conn.cursor().execute(query, (path,))
        self.conn.commit()
        return

    def update_entry(self, entry):
        """Updates given entry in database"""
        query = f"UPDATE {TABLE_FILES} SET {COLUMN_FREQUENCY}=?, {COLUMN_KEY}=? WHERE {COLUMN_PATH}=?"
        self.conn.cursor().execute(query, (entry.frequency, entry.key.value, entry.path))
        self.conn.commit()


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
