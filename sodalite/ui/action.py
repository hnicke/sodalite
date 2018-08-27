from typing import List, Callable

from core import config
from ui import viewmodel
from ui.viewmodel import Mode

# global actions
exit = "exit"
abort = "abort"
navigate_mode = "navigate_mode"
assign_mode = "assign_mode"
operate_mode = "operate_mode"
filter = "filter"
toggle_dotfiles = "toggle_dotifles"
scroll_page_down = "scroll_page_down"
scroll_page_up = "scroll_page_up"
scroll_half_page_down = "scroll_half_page_down"
scroll_half_page_up = "scroll_half_page_up"
yank_current_path = "yank_current_path"
yank_file_content = "yank_file_content"

# normal mode actions
go_to_parent = "go_to_parent"
go_to_home = "go_to_home"
go_to_root = "go_to_root"
go_to_previous = "go_to_previous"
go_to_next = "go_to_next"

# assign mode actions
select_next = "select_next"
select_previous = "select_previous"

# operate mode actions
yank = 'yank'
paste = 'paste'
delete = 'delete'
rename = 'rename'

default_keybindings = {
    # global
    exit: 'enter',
    abort: 'ctrl c',
    navigate_mode: 'esc',
    assign_mode: '=',
    operate_mode: ' ',
    filter: '/',
    toggle_dotfiles: 'meta h',
    scroll_page_down: 'ctrl f',
    scroll_page_up: 'ctrl b',
    scroll_half_page_down: 'ctrl d',
    scroll_half_page_up: 'ctrl u',
    yank_current_path: 'ctrl y',
    yank_file_content: 'meta y',

    # navigate mode
    go_to_parent: '.',
    go_to_home: ';',
    go_to_root: ',',
    go_to_previous: 'backspace',  # also matches 'ctrl h'
    go_to_next: 'ctrl l',

    # assign mode
    select_next: 'ctrl n',
    select_previous: 'ctrl p',

    # operate mode
    yank: 'y',
    paste: 'p',
    delete: 'd',
    rename: 'r',
}


class Action:

    def __init__(self, name, action: Callable, modes: List[Mode] = None):
        self.name = name
        self.is_global = not modes
        self.modes = modes
        self.action = action
        self.keybinding = config.keymap.setdefault(name, default_keybindings[name])

    def handle(self, input: str):
        if input == self.keybinding:
            if self.is_global or viewmodel.global_mode in self.modes:
                self.action.__call__()
                return True


class MultiAction(Action):

    def __init__(self, name, action: Callable, modes: List[Mode] = None):
        super().__init__(name, action, modes=modes)
