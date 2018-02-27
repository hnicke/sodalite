import curses
import logging
import os
from typing import List, Dict

from core.config import Config

logger = logging.getLogger(__name__)

special_keys = {'ENTER': '^J'
                }


class HookEngine:

    def __init__(self, config: Config):
        self.hooks = HookMap(config.hooks)

    def get_hooks(self, entry) -> List['Hook']:
        """
        :return: list of possible actions for given entry
        """
        hooks = []
        hooks.extend(self.hooks.get_general_hooks())
        if entry.is_dir():
            hooks.extend(self.hooks.get_dir_hooks())
        elif entry.is_file():
            extension = os.path.splitext(entry.name)[1].lower().replace(".", "")
            hooks.extend(self.hooks.get_custom_hooks().get(extension, []))
            hooks.extend(self.hooks.get_file_hooks())
            if entry.is_plain_text_file():
                hooks.extend(self.hooks.get_plain_text_hooks())
        return hooks

    def is_hook(self, key: str, entry) -> bool:
        matches = [hook for hook in entry.hooks if hook.key.lower() == key.lower()]
        return len(matches) > 0

    def trigger_hook(self, key: str, entry):
        hook = [hook for hook in entry.hooks if hook.key.lower() == key.lower()][0]
        hook.trigger(entry)


class HookMap:
    def __init__(self, hooks: dict):
        self.map: Dict[str, List[Hook]] = {}
        self.custom: Dict[str, List[Hook]] = {}

        for category in ['general', 'dir', 'file', 'plain_text']:
            self.map[category] = []
            if hooks[category] is None:
                continue
            for key, hook_definition in hooks[category].items():
                hook = _extract_hook(key, hook_definition)
                self.map[category].append(hook)

        if hooks['custom'] is not None:
            for category in hooks['custom'].values():
                for key, hook_definition in category['hooks'].items():
                    hook = _extract_hook(key, hook_definition)
                    for extension in category['extensions']:
                        hook_list = self.custom.get(extension, [])
                        hook_list.append(hook)
                        self.custom[extension] = hook_list

    def get_general_hooks(self) -> List['Hook']:
        return self.map['general']

    def get_dir_hooks(self) -> List['Hook']:
        return self.map['dir']

    def get_file_hooks(self) -> List['Hook']:
        return self.map['file']

    def get_plain_text_hooks(self) -> List['Hook']:
        return self.map['plain_text']

    def get_custom_hooks(self) -> Dict[str, List['Hook']]:
        return self.custom

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "general: {}, dir: {}, file: {} plain_text: {}, custom: {}".format(self.get_general_hooks(),
                                                                                  self.get_dir_hooks(),
                                                                                  self.get_file_hooks(),
                                                                                  self.get_plain_text_hooks(),
                                                                                  self.custom)


def _extract_hook(key: str, hook_definition: [dict, str]) -> 'Hook':
    if type(hook_definition) is dict:
        hook = Hook(key, hook_definition['action'], label=hook_definition.get('label'))
    else:
        hook = Hook(key, hook_definition)
    return hook


class Hook:
    def __init__(self, key: str, action: str, label=None):
        self.key = special_keys.get(key, key)
        self.label = label
        self.finally_exit = False
        if action.endswith("#q"):
            self.finally_exit = True
            action = action[:-2]
        self.action = action

    def __str__(self):
        return "<key: '{}', hook: '{}', label: '{}'>".format(self.key, self.action, self.label)

    def __repr__(self):
        return str(self)

    def trigger(self, entry):
        os.environ['entry'] = entry.path
        logger.info("Executing command: {}".format(self.action))
        entry.chdir()
        curses.endwin()
        result = os.system(self.action)
        logger.info(f"Result is {result}")
        if self.finally_exit:
            exit(0)

