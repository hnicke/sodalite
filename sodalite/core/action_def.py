from enum import Enum


class ActionName(Enum):
    # global actions
    exit = "exit"
    abort = "abort"
    navigate_mode = "navigate_mode"
    assign_mode = "assign_mode"
    operate_mode = "operate_mode"
    filter = "filter"
    toggle_hidden_files = "toggle_hidden_files"
    scroll_page_down = "scroll_page_down"
    scroll_page_up = "scroll_page_up"
    scroll_half_page_down = "scroll_half_page_down"
    scroll_half_page_up = "scroll_half_page_up"
    yank_current_path = "yank_current_path"
    yank_file_content = "yank_file_content"
    show_help = 'show_help'

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

    def __str__(self) -> str:
        return self.value.replace('_', ' ')

    def __repr__(self) -> str:
        return f"Action '{self.value}'"


default_keybindings = {
    # global
    ActionName.exit: 'enter',
    ActionName.abort: 'ctrl c',
    ActionName.navigate_mode: 'esc',
    ActionName.assign_mode: '=',
    ActionName.operate_mode: ' ',
    ActionName.filter: '/',
    ActionName.toggle_hidden_files: 'meta h',
    ActionName.scroll_page_down: 'ctrl f',
    ActionName.scroll_page_up: 'ctrl b',
    ActionName.scroll_half_page_down: 'ctrl d',
    ActionName.scroll_half_page_up: 'ctrl u',
    ActionName.yank_current_path: 'ctrl y',
    ActionName.yank_file_content: 'meta y',
    ActionName.show_help: '?',

    # navigate mode
    ActionName.go_to_parent: '.',
    ActionName.go_to_home: ';',
    ActionName.go_to_root: ',',
    ActionName.go_to_previous: 'backspace',  # also matches 'ctrl h'
    ActionName.go_to_next: 'ctrl l',

    # assign mode
    ActionName.select_next: 'ctrl n',
    ActionName.select_previous: 'ctrl p',

    # operate mode
    ActionName.yank: 'y',
    ActionName.paste: 'p',
    ActionName.delete: 'd',
    ActionName.rename: 'r',
}
