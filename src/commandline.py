import npyscreen
import curses
from mylogger import logger
import datamodel

class Commandline(npyscreen.Textfield):
    
    def __init__( self, screen, data, *args, **keywords ):
        super(Commandline, self).__init__(screen, *args, **keywords)
        self.data = data
        self.search_mode = False

    def t_filter( self, input ):
        char = chr(input)
        return self.search_mode or char == '/'

    def trigger( self, input ):
        if self.search_mode == False:
            self.important = True
            self.search_mode = True
            self.value = ""
            self.update()
        if input == curses.ascii.ESC:
            self.search_mode = False
            self.value = ""
            self.data.filter( "" )
            self.parent.redraw()
        elif input == curses.ascii.BS or input == 263: #backspace
            self.value = self.value[:-1]
            if self.value == "":
                self.search_mode = False
                self.important = False
            self.data.filter( self.value[1:] )
            self.parent.redraw()
        elif input == curses.ascii.NL:
            self.search_mode = False
            self.important = False
            self.update()

        else:
            char = chr(input)
            self.value += char
            self.data.filter( self.value[1:] )
            self.parent.redraw()

    # clears the search and also any applied filter on data
    def clear_search( self ):
        self.search_mode = False
        self.important = False
        self.value = ""
        self.data.filter( "" )
        self.update()



