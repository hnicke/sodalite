import logging
import os
from typing import Dict, Union, TYPE_CHECKING

from sodalite.core import config

if TYPE_CHECKING:
    from sodalite.core.entry import Entry

logger = logging.getLogger(__name__)

special_keys: Dict[str, str] = {}


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
        os.environ['entry'] = str(entry.path)
        logger.info("Executing command: {}".format(self.action))
        result = os.system(f"( {self.action} ) > /dev/tty < /dev/tty")
        logger.info(f"Result is {result}")
        from sodalite.ui import graphics
        if self.finally_exit:
            graphics.exit(cwd=entry.path)
        else:
            graphics.resume()


def _extract_hook(key: str, hook_definition: Union[dict, str]) -> Hook:
    if isinstance(hook_definition, dict):
        hook = Hook(key, hook_definition['action'], label=hook_definition.get('label'))
    else:
        hook = Hook(key, hook_definition)
    return hook


class HookMap:
    def __init__(self, hooks: Dict[str, Dict[str, Union[Dict[str, str], str]]]):
        self.map: Dict[str, list[Hook]] = {}
        self.custom: Dict[str, list[Hook]] = {}

        for category in ['general', 'dir', 'file', 'plain_text', 'executable']:
            self.map[category] = []
            if hooks.get(category) is None:
                continue
            for key, hook_definition in hooks[category].items():
                hook = _extract_hook(key, hook_definition)
                self.map[category].append(hook)

        custom_hooks = hooks['custom']
        if custom_hooks is not None:
            for category in custom_hooks.values():  # type: ignore
                for key, hook_definition in category['hooks'].items():  # type: ignore
                    hook = _extract_hook(key, hook_definition)
                    for extension in category['extensions']:  # type: ignore
                        hook_list = self.custom.get(extension, [])
                        hook_list.append(hook)
                        self.custom[extension] = hook_list

    def get_general_hooks(self) -> list[Hook]:
        return self.map['general']

    def get_dir_hooks(self) -> list[Hook]:
        return self.map['dir']

    def get_file_hooks(self) -> list[Hook]:
        return self.map['file']

    def get_plain_text_hooks(self) -> list[Hook]:
        return self.map['plain_text']

    def get_executable_hooks(self) -> list[Hook]:
        return self.map['executable']

    def get_custom_hooks(self) -> Dict[str, list[Hook]]:
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


hook_map = HookMap(config.hooks)


def get_hooks(entry) -> list[Hook]:
    """
    :return: list of possible actions for given entry
    """
    matching_hooks: Dict[str, Hook] = {}
    matching_hooks.update(as_dict(hook_map.get_general_hooks()))
    if entry.is_dir():
        matching_hooks.update(as_dict(hook_map.get_dir_hooks()))
    elif entry.is_file():
        matching_hooks.update(as_dict(get_custom_hooks(entry)))
        matching_hooks.update(as_dict(hook_map.get_file_hooks()))
        if entry.is_plain_text_file():
            matching_hooks.update(as_dict(hook_map.get_plain_text_hooks()))
        if entry.executable:
            matching_hooks.update(as_dict(hook_map.get_executable_hooks()))
    return list(matching_hooks.values())


def as_dict(hook_list: list[Hook]) -> Dict[str, Hook]:
    d = {}
    for hook in hook_list:
        d[hook.key] = hook
    return d


def get_custom_hooks(entry) -> list[Hook]:
    custom_hooks = hook_map.get_custom_hooks()
    matches = list(filter(lambda x: entry.name.endswith(x), custom_hooks.keys()))
    matching_hooks: list[Hook] = []
    for match in matches:
        matching_hooks += custom_hooks[match]
    return matching_hooks


def is_hook(key: str, entry: 'Entry') -> bool:
    matches = [hook for hook in entry.hooks if hook.key.lower() == key.lower()]
    return len(matches) > 0


def trigger_hook(key: str, entry: 'Entry'):
    hook = [hook for hook in entry.hooks if hook.key.lower() == key.lower()][0]
    hook.trigger(entry)
