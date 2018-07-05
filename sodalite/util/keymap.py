from enum import Enum

from core import config

_keymap = dict((str(v), k) for (k, v) in config.keymap.items())

# ctrl h is backspace in terminal emulators
if 'ctrl h' in _keymap:
    _keymap['backspace'] = _keymap['ctrl h']


class Action(Enum):
    EXIT = 'global.exit'
    ABORT = 'global.abort'
    FILTER = 'global.filter'
    TOGGLE_DOTFILES = 'global.toggle_dotfiles'
    SCROLL_PAGE_DOWN = 'global.scroll_page_down'
    SCROLL_PAGE_UP = 'global.scroll_page_up'
    SCROLL_HALF_PAGE_DOWN = 'global.scroll_half_page_down'
    SCROLL_HALF_PAGE_UP = 'global.scroll_half_page_up'
    GO_TO_PARENT = 'normal.go_to_parent'
    GO_TO_HOME = 'normal.go_to_home'
    GO_TO_ROOT = 'normal.go_to_root'
    GO_TO_PREVIOUS = 'normal.go_to_previous'
    GO_TO_NEXT = 'normal.go_to_next'
    YANK_CURRENT_PATH = 'normal.yank_current_path'
    ASSIGN_MODE = 'normal.assign_mode'
    EDIT_MODE = 'normal.edit_mode'
    SELECT_NEXT = 'assign.select_next'
    SELECT_PREVIOUS = 'assign.select_previous'


defaults = {
    'enter': Action.EXIT,
    'ctrl c': Action.ABORT,
    '/': Action.FILTER,
    'meta h': Action.TOGGLE_DOTFILES,
    'ctrl f': Action.SCROLL_PAGE_DOWN,
    'ctrl b': Action.SCROLL_PAGE_UP,
    'ctrl d': Action.SCROLL_HALF_PAGE_DOWN,
    'ctrl u': Action.SCROLL_HALF_PAGE_UP,
    '.': Action.GO_TO_PARENT,
    ';': Action.GO_TO_HOME,
    ',': Action.GO_TO_ROOT,
    'backspace': Action.GO_TO_PREVIOUS,  # also matches 'ctrl h'
    'ctrl l': Action.GO_TO_NEXT,
    'ctrl y': Action.YANK_CURRENT_PATH,
    '=': Action.ASSIGN_MODE,
    'ctrl n': Action.SELECT_NEXT,
    'ctrl p': Action.SELECT_PREVIOUS,
    ' ': Action.EDIT_MODE,
}

for key, action in defaults.items():
    _keymap.setdefault(key, action.value)


def matches(action: Action, key: str):
    return action.value == _keymap.get(key)
