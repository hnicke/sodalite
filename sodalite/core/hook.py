import logging
import os
from typing import List, Dict

import urwid

from core import config
from ui import app
from util import environment

logger = logging.getLogger(__name__)

special_keys = {}


class Hook:
    def __init__(self, key: str, action: str, label=None):
        key = str(key)
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
        app.pause()
        result = os.system(self.action)
        app.resume()
        logger.info(f"Result is {result}")
        if self.finally_exit:
            environment.append_to_cwd_pipe(entry.path)
            app.exit()


def _extract_hook(key: str, hook_definition: [dict, str]) -> 'Hook':
    if type(hook_definition) is dict:
        hook = Hook(key, hook_definition['action'], label=hook_definition.get('label'))
    else:
        hook = Hook(key, hook_definition)
    return hook


class HookMap:
    def __init__(self, hooks: dict):
        self.map: Dict[str, List[Hook]] = {}
        self.custom: Dict[str, List[Hook]] = {}

        for category in ['general', 'dir', 'file', 'plain_text', 'executable']:
            self.map[category] = []
            if hooks.get(category) is None:
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

    def get_executable_hooks(self) -> List['Hook']:
        return self.map['executable']

    def get_custom_hooks(self) -> Dict[str, List['Hook']]:
        return self.custom

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "general: {}, dir: {}, file: {} plain_text: {}, executable: {}, custom: {}".format(
            self.get_general_hooks(),
            self.get_dir_hooks(),
            self.get_file_hooks(),
            self.get_plain_text_hooks(),
            self.get_executable_hooks(),
            self.custom)


hooks = HookMap(config.hooks)


def get_hooks(entry) -> List['Hook']:
    """
    :return: list of possible actions for given entry
    """
    matching_hooks = []
    matching_hooks.extend(hooks.get_general_hooks())
    if entry.is_dir():
        matching_hooks.extend(hooks.get_dir_hooks())
    elif entry.is_file():
        extension = os.path.splitext(entry.name)[1].lower().replace(".", "")
        matching_hooks.extend(hooks.get_custom_hooks().get(extension, []))
        matching_hooks.extend(hooks.get_file_hooks())
        if entry.is_plain_text_file():
            matching_hooks.extend(hooks.get_plain_text_hooks())
        if entry.executable:
            matching_hooks.extend(hooks.get_executable_hooks())
    return matching_hooks


def is_hook(key: str, entry) -> bool:
    matches = [hook for hook in entry.hooks if hook.key.lower() == key.lower()]
    return len(matches) > 0


def trigger_hook(key: str, entry):
    hook = [hook for hook in entry.hooks if hook.key.lower() == key.lower()][0]
    hook.trigger(entry)
