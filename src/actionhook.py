import config
import os
from mylogger import logger
import sys
import curses
import main

special_keys= { 'ENTER': '^J'
            }

class ActionEngine:

    def __init__(self, config):
        self.config = config
        actionmap = config.get_actionmap() 
        self.general_actions = self.extract_actions(actionmap.general)
        self.dir_actions = self.extract_actions(actionmap.dir)
        self.text_actions = self.extract_actions(actionmap.text)
        self.extension_actions = {}
        for extension in actionmap.extensions.keys():
            self.extension_actions[extension] = self.extract_actions(actionmap.extensions[extension])

    def trigger_action(self, key, entry):
        matches = [action.hook for action in self.get_actions(entry) if action.key.lower() == key.lower()]
        hook = matches[0]
        filename = entry.get_absolute_path()
        hook = hook.replace("#f", filename)
        finally_exit = False
        if hook.endswith("#q"):
            finally_exit = True
            hook = hook[:-2]
        if entry.is_file():
            cwd = os.path.dirname(entry.get_absolute_path())
        else:
            cwd = entry.get_absolute_path()
        os.chdir(cwd)
        os.system("{}".format(hook))
        if finally_exit:
            main.append_to_cwd_pipe( "." )
            sys.exit(0)

    # returns list of possible actions for given entry
    def get_actions( self, entry ):
        actions = []
        extension = os.path.splitext(entry.name)[1].lower().replace(".", "")
        actions.extend(self.general_actions)
        if entry.is_file():
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
        return "general: {}, dir: {}, text: {}, extensions: {}".format(self.general, self.dir, self.text, self.extensions)
        
class Action:

    def __init__(self, key, hook, description):
        self.key = special_keys.get(key, key)
        self.hook = hook
        self.description = description

    def __str__(self):
        return "<key: '{}', hook: '{}', description: '{}'>".format(self.key, self.hook, self.description)

    def __repr__(self):
        return str(self)
