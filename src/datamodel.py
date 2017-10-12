from mylogger import logger
import re

class DataModel:
    def __init__( self, entries ):
        self.entries = entries
        self.filtered_entries = []
        self.filtered_entries.extend(self.entries)
        self.filter_string = ""

    def set_entries( self, entries ):
        self.entries = entries
        self.filter_string = ""
        self.filter( "" )

    def filter ( self, filter_string ):
        if filter_string[-1:] == "\\":
            return
        self.filtered_entries.clear()
        p = re.compile(filter_string, re.IGNORECASE)
        for entry in self.entries:
            if p.search(entry.name):
                self.filtered_entries.append( entry )
        self.filter_string = filter_string

    def get_filtered_entries( self ):
        return self.filtered_entries



