#!/bin/env python
import sqlite3
import os
import entry as entry_module
import key
from mylogger import logger


class Core:

    def __init__(self, cwd="/" ):
        home = os.getenv('HOME')
        self.conn = sqlite3.connect(os.environ['SODALITE_DB_PATH'])
        self.current_entry = self.get_entry( home )


    def shutdown(self):
        self.conn.close()


    def update_entry ( self, entry ):
        self.conn.cursor().execute("UPDATE files SET frequency=?, key=?  WHERE name=? AND parent=?", (entry.frequency, entry.key.value, entry.name, entry.parent))
        self.conn.commit()

    def retrieve_entries_from_filesystem( self, entry ):
        filelist = []
        dirlist = []
        path = entry.get_absolute_path()
        for (dirpath, dirnames, filenames) in os.walk( path ):
            filelist = filenames
            dirlist = dirnames
            break
        entries = []
        for file in dirlist:
            new_entry = entry_module.Entry( file, path )
            new_entry.type = "dir"
            entries.append(new_entry)
        for file in filelist:
            new_entry = entry_module.Entry( file, path )
            new_entry.type = "file"
            entries.append(new_entry)
        return entries

    def retrieve_entries_from_db ( self, entry ):
        entries = []
        path = entry.get_absolute_path()
        cursor = self.conn.cursor().execute( "SELECT name,key,frequency FROM files WHERE parent=?", (path,))
        for row in cursor:
            new_entry = entry_module.Entry ( row[0], path )
            new_entry.key = key.Key(row[1])
            new_entry.frequency = row[2]
            entries.append(new_entry)
        return entries

    def add_new_entries_to_db( self, entries_filesystem, entries_db ):
        new_entries = list(set(entries_filesystem) - set(entries_db))
        key.assign_keys(new_entries, entries_db)
        for entry in new_entries:
            self.conn.cursor().execute("INSERT INTO files VALUES (?,?,?,?)", (entry.name, entry.parent, entry.key.value, entry.frequency))
            self.conn.commit()
        entries_db.extend(new_entries)
        return 

    # deletes obsolete entries in the db
    def remove_old_entries( self, entries_filesystem, entries_db ):
        obsolete_entries = list(set(entries_db) - set(entries_filesystem))
        for entry in obsolete_entries:
            self.conn.cursor().execute("DELETE FROM files WHERE name=? AND parent=?", (entry.name, entry.parent))
        self.conn.commit()
        return

    # attention: this method changes entries_filesystem. after calling, this variable does not reflect the entries of the filesystem anymore!! Use the returned value.
    def unite_data( self, entries_filesystem, entries_db ):
        entries = []
        for entry_fs in entries_filesystem:
            matches = [ x for x in entries_db if x == entry_fs ]
            if len(matches) == 1:
                entry_db = matches[0]
                entries_db.remove(entry_db)
                entry_fs.key = entry_db.key
                entry_fs.frequency = entry_db.frequency
                entries.append(entry_fs)
            elif len(matches) > 1:
                raise ValueError('Error, multiple matches found. constraint: uniqueness of entries') 
            else:
                print('couldnt find match for entry_fs: {}'.format(entry_fs))
        return entries

    def visit_entry( self, entry ):
        logger.info("visitting entry {}".format(entry))
        self.current_entry = entry
        entry.frequency += 1
        self.update_entry( entry )
        entries_filesystem = self.retrieve_entries_from_filesystem( entry )
        entries_db = self.retrieve_entries_from_db( entry )

        self.add_new_entries_to_db( entries_filesystem, entries_db )
        
        self.remove_old_entries( entries_filesystem, entries_db )
        entries = self.unite_data( entries_filesystem, entries_db )
        entry_module.sort(entries)
        self.current_entry.children = entries

    def change_to_key( self, key):
        if key == '.':
            parent = self.current_entry.parent
            parent_entry = self.get_entry( parent )
            self.visit_entry(parent_entry)
        else:
            matches = [x for x in self.current_entry.children if x.key.value == key]
            if len(matches) > 0:
                self.visit_entry( matches[0] )
            else:
                logger.debug("no match found for key '{}'".format(key))
        return

    # assigns given entry the new key. if the new key is already taken by another entry on the same level,
    # keys are swapped
    def assign_key(self, entry, char ):
        new_key = key.Key( char )
        old_key = entry.key
        entry.key = new_key
        self.update_entry( entry )
        conflicts = [ x for x in self.current_entry.children if x.key == new_key and x != entry ]
        if len(conflicts) == 1:
            conflict = conflicts[0]
            conflict.key = old_key
            self.update_entry( conflict)
            logger.debug("Swapped key of conflicting entry '{}'".format(conflict))
        elif len(conflicts) > 1 :
            logger.error("While swapping keys, encountered too many conflicts. Database is corrupted")
        else:
            pass
        return

# returns an entry object which matches given absolute path
# needs a database connection object in order to also retrieve frequency and key of value
    def get_entry( self, path ):
        name = os.path.basename( path)
        parent = os.path.dirname ( path )
        entry = entry_module.Entry( name, parent)
        cursor = self.conn.execute("SELECT key,frequency FROM files WHERE name=? and parent=?", (entry.name, entry.parent))
        match = cursor.fetchone()
        if match is not None:
            entry.frequency = match[1]
            entry.key = key.Key( match[0] )
        return entry
