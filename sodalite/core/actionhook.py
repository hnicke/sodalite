import curses
import os

import npyscreen

from core.config import Config
from mylogger import logger

special_keys = {'ENTER': '^J'
                }


class ActionEngine:

    def __init__(self, config: Config):
        self.config = config
        action_map = self.config.get_actionmap()
        self.general_actions = self.extract_actions(action_map.general)
        self.dir_actions = self.extract_actions(action_map.dir)
        self.text_actions = self.extract_actions(action_map.text)
        self.extension_actions = {}
        for extension in action_map.extensions.keys():
            self.extension_actions[extension] = self.extract_actions(action_map.extensions[extension])

    def trigger_action(self, key, entry):
        matches = [action.hook for action in self.get_actions(entry) if action.key.lower() == key.lower()]
        hook = matches[0]
        hook = hook.replace("#f", entry.path)
        finally_exit = False
        if hook.endswith("#q"):
            finally_exit = True
            hook = hook[:-2]
        logger.info("hook is {}".format(hook))
        self.reset_terminal()
        os.system("{}".format(hook))
        if finally_exit:
            import main
            main.clean_exit()

    def reset_terminal(self):
        """These directives make sure to reset the terminal
        note: somehow, undoing these changes on resume is not necessary, everything seems to work
        """
        screen = npyscreen.npyssafewrapper._SCREEN
        screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    # returns list of possible actions for given entry
    def get_actions(self, entry):
        actions = []
        extension = os.path.splitext(entry.name)[1].lower().replace(".", "")
        actions.extend(self.general_actions)
        if not entry.isdir:
            actions.extend(self.extension_actions.get(extension, []))
            if entry.is_plain_text_file():
                actions.extend(self.text_actions)
        else:
            # entry is dir
            actions.extend(self.dir_actions)
        return actions

    def extract_actions(self, map):
        dir_actions = []
        for key in map.keys():
            hook = map[key][0]
            description = map[key][1]
            action = Action(key, hook, description)
            dir_actions.append(action)
        return dir_actions


class ActionMap:
    def __init__(self):
        self.general = {}
        self.dir = {}
        self.text = {}
        self.extensions = {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "general: {}, dir: {}, text: {}, extensions: {}".format(self.general, self.dir, self.text,
                                                                       self.extensions)


class Action:

    def __init__(self, key, hook, description):
        self.key = special_keys.get(key, key)
        self.hook = hook
        self.description = description

    def __str__(self):
        return "<key: '{}', hook: '{}', description: '{}'>".format(self.key, self.hook, self.description)

    def __repr__(self):
        return str(self)
