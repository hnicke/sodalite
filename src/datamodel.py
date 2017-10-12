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
        #filter_string = filter_string.lower()
        #if self.filter_string != "" and filter_string != "" and self.filter_string in filter_string:
        #    logger.info("optimized. len filtered entries: {}".format(len(self.filtered_entries)))
        #    self.filtered_entries[:] = [x for x in self.filtered_entries if filter_string in x.name.lower()]
        # rebuild filter list from scratch
        if filter_string[-1:] == "\\":
            return
        self.filtered_entries.clear()
        p = re.compile(filter_string, re.IGNORECASE)
        for entry in self.entries:
            if p.search(entry.name):
            #if filter_string in entry.name.lower():
                self.filtered_entries.append( entry )
        self.filter_string = filter_string

    def get_filtered_entries( self ):
        return self.filtered_entries



