import curses

import npyscreen

from core import hook as hook_module
from core.hook import HookEngine
from ui import entrypane


class ActionPane(entrypane.EntryPane, npyscreen.Pager):

    def __init__(self, *args, data, **keywords):
        self.data = data
        npyscreen.Pager.__init__(self, *args, **keywords)
        entrypane.EntryPane.__init__(self)

        self.hook_engine: HookEngine = self.parent.hook_engine

        self.handlers = {}

    def is_action_trigger(self, input):
        key = curses.ascii.unctrl(input)
        return self.hook_engine.is_hook(key, self.data.current_entry)

    def trigger_hook(self, input):
        key = curses.ascii.unctrl(input)
        self.hook_engine.trigger_hook(key, self.data.current_entry)

    def adjust_handlers(self):
        for action in self.values:
            trigger = self.create_trigger_function(action.hook)
            handler = (action.key, trigger)
            self.handlers[action.key] = trigger

    def display_value(self, hook):
        print_key = hook.key
        for name, key in hook_module.special_keys.items():
            if key == hook.key:
                print_key = name
                break
        return "{}{}".format(print_key.ljust(7), hook.label.ljust(30))

    def when_parent_changes_value(self):
        self.values = self.data.hooks
