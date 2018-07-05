from enum import Enum
from typing import Dict

from core import config
from ui import viewmodel
from ui.viewmodel import Mode


class Action(Enum):
    pass


class GlobalAction(Action):
    exit = 1
    abort = 2
    filter = 3
    toggle_dotfiles = 4
    scroll_page_down = 5
    scroll_page_up = 6
    scroll_half_page_down = 7
    scroll_half_page_up = 8
    yank_current_path = 9
    normal_mode = 10


class NormalAction(Action):
    go_to_parent = 1
    go_to_home = 2
    go_to_root = 3
    go_to_previous = 4
    go_to_next = 5
    assign_mode = 6
    edit_mode = 7


class AssignAction(Action):
    select_next = 1
    select_previous = 2
    abort = 3


class EditAction(Action):
    pass


MODE_TO_ACTION_TYPE = {
    Mode.NORMAL: NormalAction,
    Mode.ASSIGN_CHOOSE_KEY: AssignAction,
    Mode.ASSIGN_CHOOSE_ENTRY: AssignAction,
    Mode.EDIT: EditAction
}

KEYMAP_TO_ACTION = {
    config.KEY_KEYMAP_GLOBAL: GlobalAction,
    config.KEY_KEYMAP_NORMAL: NormalAction,
    config.KEY_KEYMAP_ASSIGN: AssignAction,
    config.KEY_KEYMAP_EDIT: EditAction,
}

defaults = {
    GlobalAction.exit: 'enter',
    GlobalAction.abort: 'ctrl c',
    GlobalAction.filter: '/',
    GlobalAction.toggle_dotfiles: 'meta h',
    GlobalAction.scroll_page_down: 'ctrl f',
    GlobalAction.scroll_page_up: 'ctrl b',
    GlobalAction.scroll_half_page_down: 'ctrl d',
    GlobalAction.scroll_half_page_up: 'ctrl u',
    GlobalAction.yank_current_path: 'ctrl y',
    GlobalAction.normal_mode: 'esc',

    NormalAction.go_to_parent: '.',
    NormalAction.go_to_home: ';',
    NormalAction.go_to_root: ',',
    NormalAction.go_to_previous: 'backspace',  # also matches 'ctrl h'
    NormalAction.go_to_next: 'ctrl l',
    NormalAction.assign_mode: '=',
    NormalAction.edit_mode: ' ',

    AssignAction.select_next: 'ctrl n',
    AssignAction.select_previous: 'ctrl p',
    AssignAction.abort: 'esc'
}

_keymap: Dict[type, Dict[str, Action]] = {}

for textual_mode, bindings in config.keymap.items():
    action_type = KEYMAP_TO_ACTION[textual_mode]
    # ctrl h is backspace in terminal emulators
    for action, keybinding in bindings.items():
        if keybinding == 'ctrl h':
            _keymap[action_type][action] = 'ctrl h'
    _keymap[action_type] = dict((str(v), action_type[k]) for (k, v) in bindings.items())

for action, keybinding in defaults.items():
    _keymap[action.__class__].setdefault(keybinding, action)


def get_action(keybinding: str) -> Action:
    """

    :param keybinding:
    :return: None if no action is bound to given keybinding
    """
    action_type = MODE_TO_ACTION_TYPE[viewmodel.global_mode.mode]
    action = None
    if keybinding in _keymap[action_type]:
        action = _keymap[action_type][keybinding]
    elif keybinding in _keymap[GlobalAction]:
        action = _keymap[GlobalAction][keybinding]
    return action
