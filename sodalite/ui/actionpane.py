import curses

import npyscreen

from core import actionhook
from ui import entrypane


class ActionPane(entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.navigator = self.parent.parentApp.navigator
        self.action_engine = self.parent.parentApp.action_engine

        self.handlers = {}

    def is_action_trigger(self, input):
        key = curses.ascii.unctrl(input)
        return key in [action.key for action in self.values]

    def trigger_action(self, input):
        key = curses.ascii.unctrl(input)
        current_entry = self.navigator.current_entry
        self.action_engine.trigger_action(key, current_entry)

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
        return "{}{}".format(print_key.ljust(7), action.description.ljust(30))

    def when_parent_changes_value(self):
        current_entry = self.parent.navigator.current_entry
        self.values = self.parent.parentApp.action_engine.get_actions(current_entry)
