import logging
from pathlib import Path
from typing import Callable, Tuple
from typing import TYPE_CHECKING

import pyperclip
from urwid import AttrSpec

from sodalite.core import key as key_module, hook, buffer, operate, Navigator
from sodalite.core.key import Key
from sodalite.ui import graphics, viewmodel, notify, theme, action
from sodalite.ui.action import Action
from sodalite.ui.viewmodel import Mode, ViewModel
from sodalite.util import env

if TYPE_CHECKING:
    from sodalite.ui.graphics import MainFrame

logger = logging.getLogger(__name__)


class Control:

    def __init__(self, frame: 'MainFrame'):
        self.action_map: dict[str, Action] = {}
        self._action_name_to_callable: dict[str, Callable] = {}
        self.action_name_to_callable = {
            action.exit: self.exit,
            action.abort: self.abort,
            action.navigate_mode: self.enter_navigate_mode,
            action.assign_mode: self.enter_assign_mode,
            action.operate_mode: self.enter_operate_mode,
            action.filter: self.trigger_filter,
            action.yank_current_path: self.yank_cwd_to_clipboard,
            action.yank_file_content: self.yank_file_content_to_clipboard,
            action.toggle_hidden_files: self.toggle_dotfiles,
            action.scroll_page_down: self.scroll_page_down,
            action.scroll_page_up: self.scroll_page_up,
            action.scroll_half_page_down: self.scroll_half_page_down,
            action.scroll_half_page_up: self.scroll_half_page_up,
            action.show_help: self.show_keys
        }

        self.frame = frame
        self.hookbox = frame.hookbox
        self.filter = frame.filter
        self.navigator: Navigator = frame.navigator
        self.model: ViewModel = frame.model
        self._list = None
        self.list_size = None
        self.filter_size = None
        self.hookbox_size = None
        self.active_action = None

    @property
    def action_name_to_callable(self):
        return self._action_name_to_callable

    @action_name_to_callable.setter
    def action_name_to_callable(self, mapping):
        self._action_name_to_callable = mapping
        self.action_map: dict[str, Action] = {k: Action(k, v) for (k, v) in mapping.items()}

    @property
    def list(self):
        return self.frame.mainpane.body

    def handle_keypress(self, size: Tuple[int, int], key: str):
        try:
            self.calculate_sizes(size)
            handled = False
            if self.filter.active:
                self.filter.keypress(self.filter_size, key)
                handled = True
            elif self.active_action:
                handled = self.active_action.__call__(key=key)

            if not handled:
                if not self.handle_key_individually(key):
                    for _action in self.action_map.values():
                        if _action.handle(key):
                            break
        except PermissionError:
            notify.show((AttrSpec(theme.forbidden + ',bold', '', colors=16), "PERMISSION DENIED"))
        except FileNotFoundError:
            notify.show((AttrSpec(theme.forbidden + ',bold', '', colors=16), "FILE NOT FOUND"))

    def handle_key_individually(self, key):
        pass

    def calculate_sizes(self, size):
        (maxcol, maxrow) = size
        remaining = maxrow
        remaining -= self.hookbox.rows((maxcol,))
        self.list_size = (maxcol, remaining)
        self.hookbox_size = (maxcol, remaining)
        self.filter_size = (maxcol,)

    def exit(self):
        graphics.exit(cwd=self.navigator.history.cwd())

    def abort(self):
        graphics.exit()

    def enter_navigate_mode(self):
        viewmodel.global_mode.mode = Mode.NAVIGATE
        self.list.render(self.list_size, True)

    def enter_assign_mode(self):
        if self.model.current_entry.is_dir:
            viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_ENTRY
            self.list.render(self.list_size, True)

    def enter_operate_mode(self):
        if self.model.current_entry.is_dir:
            viewmodel.global_mode.mode = Mode.OPERATE
            self.list.render(self.list_size, True)

    def trigger_filter(self):
        self.filter.active = True

    def scroll_page_down(self):
        self.list.scroll_page_down(self.list_size)

    def scroll_half_page_down(self):
        self.list.scroll_half_page_down(self.list_size)

    def scroll_page_up(self):
        self.list.scroll_page_up(self.list_size)

    def scroll_half_page_up(self):
        self.list.scroll_half_page_up(self.list_size)

    def yank_cwd_to_clipboard(self):
        path = self.navigator.current_entry.path
        self.yank_to_clipboard(path)

    def yank_file_content_to_clipboard(self):
        entry = self.model.current_entry
        if entry.is_plain_text_file:
            self.yank_to_clipboard(entry.content)

    def yank_to_clipboard(self, text: str):
        try:
            pyperclip.copy(text)
            text_to_log = text[0:60].replace("\n", "")
            if len(text) > 60:
                text_to_log += "..."
            logger.info(f"Yanked '{text_to_log}' to system clipboard")
            notify.show("Yanked to clipboard", duration=1)
        except pyperclip.PyperclipException:
            logger.exception("Failed to yank")
            notify.show("Failed to yank: system has no clipboard", duration=2)

    def toggle_dotfiles(self):
        self.model.show_hidden_files = not self.model.show_hidden_files
        if self.model.show_hidden_files:
            message = 'show dotfiles'
        else:
            message = 'hide dotfiles'
        notify.show(message, duration=0.7)

    def show_keys(self):
        graphics.popupLauncher.open_pop_up(self)


class NavigateControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)

        actions = {
            action.go_to_parent: self.go_to_parent,
            action.go_to_home: self.go_to_home,
            action.go_to_root: self.go_to_root,
            action.go_to_previous: self.go_to_previous,
            action.go_to_next: self.go_to_next,
        }
        actions.update(self.action_name_to_callable)
        self.action_name_to_callable = actions

    def handle_key_individually(self, key: str):
        if hook.is_hook(key, self.model.current_entry):
            hook.trigger_hook(key, self.model.current_entry)
            return True
        elif self.navigator.is_navigation_key(key):
            self.go_to_key(Key(key))
            return True

    def go_to_key(self, key: Key):
        self.navigator.visit_child(key)
        self.clear_filter()

    def go_to_parent(self):
        self.navigator.visit_parent()
        self.clear_filter()

    def go_to_home(self):
        self.navigator.visit_path(env.HOME)
        self.clear_filter()

    def go_to_root(self):
        self.navigator.visit_path(Path('/'))
        self.clear_filter()

    def go_to_previous(self):
        self.navigator.visit_previous()
        self.clear_filter()

    def go_to_next(self):
        self.navigator.visit_next()
        self.clear_filter()

    def clear_filter(self):
        filter = self.frame.mainpane.frame.footer
        if filter:
            filter.hide()


class AssignControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)
        actions = {
            action.select_next: self.list.select_next,
            action.select_previous: self.list.select_previous,
        }
        actions.update(self.action_name_to_callable)
        self.action_name_to_callable = actions

    def handle_key_individually(self, key):
        if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY and self.navigator.is_navigation_key(key):
            self.choose_entry(key)
            return True
        elif viewmodel.global_mode == Mode.ASSIGN_CHOOSE_KEY and key_module.is_navigation_key(key):
            self.assign_key(key)
            return True

    def exit(self) -> None:
        if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY:
            viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_KEY

    def choose_entry(self, key: str) -> None:
        if key in key_module.get_all_keys():
            entry = self.navigator.current_entry.get_child_for_key(Key(key))
            assert entry
            self.list.select(entry)
            viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_KEY
        elif key == 'enter':
            viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_KEY

    def assign_key(self, key: str):
        if key_module.is_navigation_key(key):
            selected_entry = self.list.selection.entry
            self.navigator.assign_key(Key(key), Path(selected_entry.path))
            self.list.on_entries_changed(self.model)
            self.enter_navigate_mode()


class OperateControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)
        self.list_entry_for_renaming = None
        actions = {
            action.yank: self.yank,
            action.paste: self.paste,
            action.delete: self.delete,
            action.rename: self.rename,
        }
        actions.update(self.action_name_to_callable)
        self.action_name_to_callable = actions

    def yank(self, key=None):
        if key:
            if self.navigator.is_navigation_key(key):
                target = self.navigator.current_entry.get_child_for_key(Key(key))
                buffer.registers[0].copy_to(target)
                notify.show(f"yanked {target.path}")
                self.active_action = None
            self.enter_navigate_mode()
        else:
            notify.show("yank what?", duration=0)
            self.active_action = self.yank

    def paste(self) -> None:
        entry = self.navigator.current_entry
        buffer.registers[0].read_from(entry)
        self.navigator.reload_current_entry()

    def delete(self, key=None):
        if key:
            if self.navigator.is_navigation_key(key):
                target = self.navigator.current_entry.get_child_for_key(Key(key))
                buffer.registers[0].move_to(target)
                self.navigator.reload_current_entry()
                self.active_action = None
                self.enter_navigate_mode()
                return True
        else:
            notify.show("delete what?", duration=0)
            self.active_action = self.delete

    def rename(self, key=None):
        if key:
            if self.list_entry_for_renaming:
                exit_action_key = self.action_map[action.exit].keybinding
                navigate_mode_action_key = self.action_map[action.navigate_mode].keybinding
                if key in (exit_action_key, navigate_mode_action_key):
                    if key == exit_action_key:
                        new_name = self.list_entry_for_renaming.edit_text
                        operate.rename(self.list_entry_for_renaming.entry, new_name)
                    self.list_entry_for_renaming.editing = False
                    self.list.render(self.list_size, focus=True)
                    self.list_entry_for_renaming = None
                    self.active_action = None
                    self.enter_navigate_mode()
                else:
                    self.list_entry_for_renaming.keypress(self.filter_size, key)
                return True
            else:
                if self.navigator.is_navigation_key(key):
                    target = self.navigator.current_entry.get_child_for_key(Key(key))
                    notify.clear()
                    list_entry = self.list.get_list_entry(target)
                    if list_entry:
                        list_entry.editing = True
                        self.list.selection = list_entry
                        self.list.render(self.list_size, focus=True)
                        self.list_entry_for_renaming = list_entry
                    return True
        else:
            notify.show("rename what?", duration=0)
            self.active_action = self.rename
