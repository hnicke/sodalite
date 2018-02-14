import npyscreen
import curses
from mylogger import logger
import datamodel

class Commandline(npyscreen.Textfield):
    
    def __init__( self, screen, data, *args, **keywords ):
        super(Commandline, self).__init__(screen, *args, **keywords)
        self.data = data
        self.search_mode = False
        self.add_handlers({
                curses.ascii.ESC: self.__reset
                })

    def t_filter( self, input ):
        try: 
            char = chr(input)
            return char == '/'
        except ValueError:
            return False

    def when_value_edited( self ):
        self.data.filter( self.value[1:] )
        self.parent.redraw()

    def trigger( self, input ):
        self.value = "/"
        self.edit()

    def __reset( self, _ ):
        self.clear_search( _ )
        self.parent.redraw()

    # clears the search and also any applied filter on data
    def clear_search( self, _ ):
        self.important = False
        self.value = ""
        self.data.filter( "" )
        self.editing = False



