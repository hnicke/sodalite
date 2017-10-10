#!/bin/env python
import sqlite3
import re
import os
import dirservice as dirservice_module
import entry as entry_module
import key
import sys
import main
from mylogger import logger

def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None



class Core:


    def __init__(self, cwd="/" ):
        self.dir_service = dirservice_module.DirService()
        self.conn = sqlite3.connect(os.environ['SODALITE_DB_PATH'])
        self.conn.create_function("REGEXP", 2, regexp)
        self.current_entry = self.get_entry( self.dir_service.getcwd() )
        self.visit_entry( self.current_entry )


    # clean shutdown of application
    # status_code: returned status code
    # pwd: new pwd for parent process
    def shutdown( self, status_code, pwd ):
        self.conn.close()
        main._append_to_cwd_pipe( pwd )
        logger.info("shutdown")
        sys.exit(0)


    def update_entry ( self, entry ):
        self.conn.cursor().execute("UPDATE files SET frequency=?, key=?  WHERE path=?", (entry.frequency, entry.key.value, entry.path))
        self.conn.commit()

    def retrieve_entries_from_filesystem( self, entry ):
        filelist = []
        dirlist = []
        for (dirpath, dirnames, filenames) in os.walk( entry.path ):
            filelist = filenames
            dirlist = dirnames
            break
        entries = []
        for file in dirlist:
            absolute_file_path = os.path.join(entry.path, file)
            new_entry = entry_module.Entry( absolute_file_path )
            entries.append(new_entry)
        for file in filelist:
            absolute_file_path = os.path.join(entry.path, file)
            new_entry = entry_module.Entry( absolute_file_path )
            entries.append(new_entry)
        return entries

    def retrieve_entries_from_db ( self, entry ):
        entries = []
        path = entry.path
        # fix regexp for root
        if path == '/':
            path = '';
        cursor = self.conn.cursor().execute( "SELECT path,key,frequency FROM files WHERE path REGEXP ?", ["^"+ path + "/[^/]+$"])
        for row in cursor:
            new_entry = entry_module.Entry ( row[0] )
            new_entry.key = key.Key(row[1])
            new_entry.frequency = row[2]
            entries.append(new_entry)
        return entries

    def add_new_entries_to_db( self, entries_filesystem, entries_db ):
        new_entries = list(set(entries_filesystem) - set(entries_db))
        key.assign_keys(new_entries, entries_db)
        for entry in new_entries:
            self.conn.cursor().execute("INSERT INTO files VALUES (?,?,?)", (entry.path, entry.key.value, entry.frequency))
            self.conn.commit()
        entries_db.extend(new_entries)
        return 

    # deletes obsolete entries in the db
    def remove_old_entries( self, entries_filesystem, entries_db ):
        obsolete_entries = list(set(entries_db) - set(entries_filesystem))
        for entry in obsolete_entries:
            self.conn.cursor().execute("DELETE FROM files WHERE path=?", (entry.path, ))
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

    def change_to_key( self, key ):
        if key == '.':
            precessor_path = self.dir_service.travel_back();
            precessor = self.get_entry( precessor_path );
            self.visit_entry( precessor )
        else:
            matches = [x for x in self.current_entry.children if x.key.value == key]
            if len(matches) > 0:
                new_dir = matches[0]
                self.dir_service.travel_to( new_dir.path )
                self.visit_entry( new_dir )
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
# connects to db to retrieve frequency and key of entry, if exists
    def get_entry( self, path ):
        entry = entry_module.Entry( path )
        cursor = self.conn.execute("SELECT key,frequency FROM files WHERE path=?", (entry.path, ))
        match = cursor.fetchone()
        if match is not None:
            entry.key = key.Key( match[0] )
            entry.frequency = match[1]
        return entry
