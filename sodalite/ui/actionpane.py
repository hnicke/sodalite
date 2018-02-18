import curses

import npyscreen

from core import action
from core.navigator import Navigator
from ui import entrypane


class ActionPane(entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, **keywords):
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.navigator: Navigator = self.parent.navigator
        self.data = self.parent.data

        self.handlers = {}

    def is_action_trigger(self, input):
        key = curses.ascii.unctrl(input)
        return self.navigator.is_action(key)

    def trigger_action(self, input):
        key = curses.ascii.unctrl(input)
        self.navigator.trigger_action(key)

    def adjust_handlers(self):
        for action in self.values:
            trigger = self.create_trigger_function(action.hook)
            handler = (action.key, trigger)
            self.handlers[action.key] = trigger

    def display_value(self, action):
        print_key = action.key
        for name, key in action.special_keys.items():
            if key == action.key:
                print_key = name
                break
        return "{}{}".format(print_key.ljust(7), action.description.ljust(30))

    def when_parent_changes_value(self):
        self.values = self.data.actions
