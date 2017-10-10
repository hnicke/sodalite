import npyscreen
import theme
import entrypane
from mylogger import logger 
import curses
import actionhook

class ActionPane(entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.core = self.parent.parentApp.core
        self.action_engine = self.parent.parentApp.action_engine

        self.handlers = {}


    def is_action_trigger(self, input):
        key = curses.ascii.unctrl(input)
        return key in [action.key for action in self.values]

    def trigger_action(self, input):
        key = curses.ascii.unctrl(input)
        current_entry = self.core.current_entry
        self.action_engine.trigger_action( key, current_entry )

    def adjust_handlers(self):
        for action in self.values:
            trigger = self.create_trigger_function(action.hook)
            handler = (action.key, trigger)
            self.handlers[action.key] = trigger

    def display_value(self, action):
        print_key = action.key
        for name, key in actionhook.special_keys.items():
            if key == action.key:
                print_key = name
                break
        return "{}{}".format(print_key.ljust(7),action.description.ljust(30))



