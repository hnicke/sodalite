import logging
from pathlib import Path
from typing import Callable, Tuple, Optional
from typing import TYPE_CHECKING

from sodalite.core import key as key_module, hook, buffer, operate, Navigator
from sodalite.core.action import Action
from sodalite.core.action_def import ActionName
from sodalite.core.entry import Entry
from sodalite.core.key import Key
from sodalite.ui import graphics, viewmodel, notify
from sodalite.ui.entrylist import EntryList
from sodalite.ui.viewmodel import Mode, ViewModel
from sodalite.util import pubsub

if TYPE_CHECKING:
    from sodalite.ui.graphics import MainFrame

logger = logging.getLogger(__name__)


def to_action_map(actions: dict[ActionName, Callable]) -> dict[ActionName, Action]:
    return {name: Action(name, callback) for name, callback in actions.items()}


class Control:

    def __init__(self, frame: 'MainFrame'):
        self.actions: dict[ActionName, Action] = to_action_map({
            ActionName.exit: self.exit,
            ActionName.abort: self.abort,
            ActionName.filter: self.trigger_filter,
            ActionName.yank_current_path: self.yank_cwd_to_clipboard,
            ActionName.yank_file_content: self.yank_file_content_to_clipboard,
            ActionName.scroll_page_down: self.scroll_page_down,
            ActionName.scroll_page_up: self.scroll_page_up,
            ActionName.scroll_half_page_down: self.scroll_half_page_down,
            ActionName.scroll_half_page_up: self.scroll_half_page_up,
            ActionName.show_help: self.show_keys
        })

        self.frame = frame
        self.hookbox = frame.hookbox
        self.filter = frame.filter
        self.navigator: Navigator = frame.navigator
        self.model: ViewModel = frame.model
        self._list = None
        self.list_size: Optional[Tuple[int, int]] = None
        self.filter_size: Optional[Tuple[int]] = None
        self.hookbox_size: Optional[Tuple[int, int]] = None
        self.active_action = None

        pubsub.entry_connect(self.on_entry_changed)

    def add_action(self, action: Action):
        self.actions[action.name] = action

    def remove_action(self, name: ActionName):
        self.actions.pop(name, None)

    def on_entry_changed(self, entry: Entry):
        actions = {
            ActionName.toggle_hidden_files: self.toggle_dotfiles,
            ActionName.operate_mode: self.enter_operate_mode,
            ActionName.navigate_mode: self.enter_navigate_mode,
            ActionName.assign_mode: self.enter_assign_mode,
        }
        if entry.is_dir:
            for name, callback in actions.items():
                self.add_action(Action(name, callback))
        else:
            for action in actions.keys():
                self.remove_action(action)

    @property
    def list(self) -> EntryList:
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
                    for _action in self.actions.values():
                        if _action.handle(key):
                            break
        except PermissionError:
            notify.show_error("PERMISSION DENIED")
        except FileNotFoundError:
            notify.show_error("FILE NOT FOUND")

    def handle_key_individually(self, key):
        pass

    def calculate_sizes(self, size: Tuple[int, int]) -> None:
        (maxcol, maxrow) = size
        remaining = maxrow
        remaining -= self.hookbox.rows((maxcol,))
        self.list_size = (maxcol, remaining)
        self.hookbox_size = (maxcol, remaining)
        self.filter_size = (maxcol,)

    def exit(self) -> None:
        graphics.exit(cwd=self.navigator.history.cwd())

    def abort(self) -> None:
        graphics.exit()

    def enter_navigate_mode(self) -> None:
        viewmodel.global_mode.mode = Mode.NAVIGATE
        self.list.render(self.list_size, True)

    def enter_assign_mode(self) -> None:
        if self.model.current_entry.is_dir:
            viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_ENTRY
            self.list.render(self.list_size, True)

    def enter_operate_mode(self) -> None:
        if self.model.current_entry.is_dir:
            viewmodel.global_mode.mode = Mode.OPERATE
            self.list.render(self.list_size, True)

    def trigger_filter(self) -> None:
        self.filter.active = True

    def scroll_page_down(self) -> None:
        self.list.scroll_page_down(self.list_size)

    def scroll_half_page_down(self) -> None:
        self.list.scroll_half_page_down(self.list_size)

    def scroll_page_up(self) -> None:
        self.list.scroll_page_up(self.list_size)

    def scroll_half_page_up(self) -> None:
        self.list.scroll_half_page_up(self.list_size)

    def yank_cwd_to_clipboard(self) -> None:
        path = self.navigator.current_entry.path
        self.yank_to_clipboard(str(path.absolute()))

    def yank_file_content_to_clipboard(self) -> None:
        entry = self.model.current_entry
        if entry.is_plain_text_file:
            self.yank_to_clipboard(entry.content)

    def yank_to_clipboard(self, text: str) -> None:
        import pyperclip
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

    def toggle_dotfiles(self) -> None:
        self.model.show_hidden_files = not self.model.show_hidden_files
        if self.model.show_hidden_files:
            message = 'show dotfiles'
        else:
            message = 'hide dotfiles'
        notify.show(message, duration=0.7)

    def show_keys(self) -> None:
        graphics.popupLauncher.open_pop_up(self)


class NavigateControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)

        actions = to_action_map({
            ActionName.go_to_parent: self.go_to_parent,
            ActionName.go_to_home: self.go_to_home,
            ActionName.go_to_root: self.go_to_root,
            ActionName.go_to_previous: self.go_to_previous,
            ActionName.go_to_next: self.go_to_next,
        })
        actions.update(self.actions)
        self.actions = actions

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
        self.navigator.visit_path(Path.home())
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
        actions = to_action_map({
            ActionName.select_next: self.list.select_next,
            ActionName.select_previous: self.list.select_previous,
        })
        actions.update(self.actions)
        self.actions = actions

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
            self.list.on_entries_changed(self.model.entries)
            self.enter_navigate_mode()


class OperateControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)
        self.list_entry_for_renaming = None
        actions = to_action_map({
            ActionName.yank: self.yank,
            ActionName.paste: self.paste,
            ActionName.delete: self.delete,
            ActionName.rename: self.rename,
        })
        actions.update(self.actions)
        self.actions = actions

    def yank(self, key=None):
        if key:
            if self.navigator.is_navigation_key(key):
                target = self.navigator.current_entry.get_child_for_key(Key(key))
                buffer.registers[0].copy_to(target)
                self.enter_navigate_mode()
                self.active_action = None
                notify.show(f"yanked {target.path.name}")
            else:
                self.enter_navigate_mode()
        else:
            notify.show("yank what?", duration=0)
            self.active_action = self.yank

    def paste(self) -> None:
        entry = self.navigator.current_entry
        buffer.registers[0].read_from(entry)
        self.navigator.reload_current_entry()
        self.enter_navigate_mode()
        notify.show("pasted file(s)")

    def delete(self, key=None):
        if key:
            if self.navigator.is_navigation_key(key):
                target = self.navigator.current_entry.get_child_for_key(Key(key))
                buffer.registers[0].move_to(target)
                self.navigator.reload_current_entry()
                self.active_action = None
                self.enter_navigate_mode()
                notify.show(f"deleted {target.path.name}")
                return True
        else:
            notify.show("delete what?", duration=0)
            self.active_action = self.delete

    def rename(self, key=None):
        if key:
            if self.list_entry_for_renaming:
                exit_action_key = self.actions[ActionName.exit].keybinding
                navigate_mode_action_key = self.actions[ActionName.navigate_mode].keybinding
                if key in (exit_action_key, navigate_mode_action_key):
                    if key == exit_action_key:
                        new_name = self.list_entry_for_renaming.edit_text
                        operate.rename(self.list_entry_for_renaming.entry, new_name)
                    self.list_entry_for_renaming.editing = False
                    self.list.render(self.list_size, focus=True)
                    self.list_entry_for_renaming = None
                    self.active_action = None
                    self.enter_navigate_mode()
                    notify.show("renamed file")
                else:
                    self.list_entry_for_renaming.keypress(self.filter_size, key)
                return True
            else:
                if self.navigator.is_navigation_key(key):
                    target = self.navigator.current_entry.get_child_for_key(Key(key))
                    notify.show(f"renaming {target.name}", duration=0)
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
