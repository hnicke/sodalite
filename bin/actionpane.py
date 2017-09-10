import npyscreen
import theme
import entrypane
from mylogger import logger
import curses

class ActionPane(entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.core = self.parent.parentApp.core
        self.action_engine = self.parent.parentApp.action_engine

        self.complex_handlers = [
                (self.is_action_trigger, self.trigger_action)
                ]
        self.add_handlers({
            ord('.'):       self.h_exit_action_pane
            })


    def is_action_trigger(self, input):
        key = curses.ascii.unctrl(input)
        return key in [action.key for action in self.values]

    def trigger_action(self, input):
        key = curses.ascii.unctrl(input)
        current_entry = self.core.current_entry
        self.action_engine.trigger_action( key, current_entry )

    def redraw(self):
        self.values = self.action_engine.get_actions(self.core.current_entry)

    def adjust_handlers(self):
        for action in self.values:
            trigger = self.create_trigger_function(action.hook)
            handler = (action.key, trigger)
            self.handlers[action.key] = trigger


    def create_trigger_function(self, hook):
        filename = self.core.current_entry.get_absolute_path()
        hook.replace("%s", filename)
        
        def trigger_function(self, input):
            #os.system(hook)
            logger.info(hook)

        return trigger_function

    def h_exit_action_pane(self, input):
        char = chr(input)
        self.core.change_to_key(char)
        self.parent.parentApp.switchForm("MAIN")

    def display_value(self, action):
        return "{}{}{}".format(action.key.ljust(4),action.description.ljust(30), action.hook)



