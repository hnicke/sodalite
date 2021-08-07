import functools
import logging
import os
from typing import Union, TYPE_CHECKING, Optional

from sodalite.core import config
from sodalite.core.config import HooksConfig
from sodalite.util import env

if TYPE_CHECKING:
    from sodalite.core.entry import Entry

logger = logging.getLogger(__name__)

special_keys: dict[str, str] = {}


class Hook:
    def __init__(self, key: str, action: str, label: Optional[str] = None) -> None:
        key = str(key)
        self.key = special_keys.get(key, key)
        self.label = label
        self.finally_exit = False
        if action.endswith("#q"):
            self.finally_exit = True
            action = action[:-2]
        self.action = action

    def __str__(self) -> str:
        return f"<key: '{self.key}', hook: '{self.action}', label: '{self.label}'>"

    def __repr__(self) -> str:
        return str(self)

    def trigger(self, entry: 'Entry') -> None:
        os.environ['entry'] = str(entry.path)
        logger.info(f"Executing command: {self.action}")
        cmd = self.action
        if env.RUNNING_IN_FLATPAK:
            # TODO this is a hack and should be addressed (see https://github.com/hnicke/sodalite/issues/240)
            if 'sodalite-open' not in cmd:
                cmd = 'flatpak-spawn --host ' + cmd
        result = os.system(f"( {cmd} ) > /dev/tty < /dev/tty")
        logger.info(f"Result is {result}")
        if result != 0:
            from sodalite.ui import notify
            notify.show_error(f"command failed with exit code {result}")
        from sodalite.ui import graphics
        if self.finally_exit:
            graphics.exit(cwd=entry.path)
        else:
            graphics.resume()


def _extract_hook(key: str, hook_definition: Union[dict[str, str], str]) -> Hook:
    if isinstance(hook_definition, dict):
        hook = Hook(key, hook_definition['action'], label=hook_definition.get('label'))
    else:
        hook = Hook(key, hook_definition)
    return hook


class HookMap:
    def __init__(self, hooks: HooksConfig):
        self.map: dict[str, list[Hook]] = {}
        self.custom: dict[str, list[Hook]] = {}

        for category in ['general', 'dir', 'file', 'plain_text', 'executable']:
            self.map[category] = []
            if hooks.get(category) is not None:
                for key, hook_definition in hooks[category].items():  # type: ignore
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

    def get_custom_hooks(self) -> dict[str, list[Hook]]:
        return self.custom

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"general: {self.get_general_hooks()}, dir: {self.get_dir_hooks()}, " \
               f"file: {self.get_file_hooks()} plain_text: {self.get_plain_text_hooks()}, " \
               f"executable: {self.get_executable_hooks()}, custom: {self.custom}"


@functools.cache
def _hook_map() -> HookMap:
    return HookMap(config.get().hooks)


def get_hooks(entry: 'Entry') -> list[Hook]:
    """
    :return: list of possible actions for given entry
    """
    hook_map = _hook_map()
    matching_hooks: dict[str, Hook] = {}
    matching_hooks.update(_as_dict(hook_map.get_general_hooks()))
    if entry.is_dir:
        matching_hooks.update(_as_dict(hook_map.get_dir_hooks()))
    elif entry.is_file:
        matching_hooks.update(_as_dict(get_custom_hooks(entry)))
        matching_hooks.update(_as_dict(hook_map.get_file_hooks()))
        if entry.is_plain_text_file:
            matching_hooks.update(_as_dict(hook_map.get_plain_text_hooks()))
        if entry.executable:
            matching_hooks.update(_as_dict(hook_map.get_executable_hooks()))
    return list(matching_hooks.values())


def _as_dict(hook_list: list[Hook]) -> dict[str, Hook]:
    d = {}
    for hook in hook_list:
        d[hook.key] = hook
    return d


def get_custom_hooks(entry: 'Entry') -> list[Hook]:
    custom_hooks = _hook_map().get_custom_hooks()
    matches = [x for x in custom_hooks.keys() if entry.name.endswith(x)]
    matching_hooks: list[Hook] = []
    for match in matches:
        matching_hooks += custom_hooks[match]
    return matching_hooks


def is_hook(key: str, entry: 'Entry') -> bool:
    matches = [hook for hook in entry.hooks if hook.key.lower() == key.lower()]
    return len(matches) > 0


def trigger_hook(key: str, entry: 'Entry') -> None:
    hook = [hook for hook in entry.hooks if hook.key.lower() == key.lower()][0]
    hook.trigger(entry)
