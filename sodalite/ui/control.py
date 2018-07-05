import logging
from typing import Callable, Dict

import pyperclip
from urwid import AttrSpec

from core import key as key_module, hook
from ui import graphics, viewmodel, notify, theme
from ui.viewmodel import Mode
from util import environment
from util import keybindings
from util.keybindings import Action, GlobalAction, NormalAction, AssignAction

logger = logging.getLogger(__name__)


class Control:

    def __init__(self, frame: 'MainFrame'):
        self.frame = frame
        self.list = frame.mainpane.body
        self.hookbox = frame.hookbox
        self.filter = frame.filter
        self.navigator = frame.navigator
        self.model = frame.model
        self.list_size = None
        self.filter_size = None
        self.hookbox_size = None
        self.ACTION_TO_CALL: Dict[Action, Callable[[]]] = {
            GlobalAction.exit: self.exit,
            GlobalAction.abort: self.abort,
            GlobalAction.filter: self.trigger_filter,
            GlobalAction.yank_current_path: self.yank_to_clipboard,
            GlobalAction.toggle_dotfiles: self.toggle_dotfiles,
            GlobalAction.scroll_page_down: self.scroll_page_down,
            GlobalAction.scroll_half_page_down: self.scroll_half_page_down,
            GlobalAction.scroll_page_up: self.scroll_page_up,
            GlobalAction.scroll_half_page_up: self.scroll_half_page_up,

        }

    def handle_keypress(self, size, key):
        try:
            self.calculate_sizes(size)
            if self.filter.active:
                self.filter.keypress(self.filter_size, key)
            elif not self.handle_key_individually(key):
                action: Action = keybindings.get_action(key)
                if action in self.ACTION_TO_CALL:
                    self.ACTION_TO_CALL[action].__call__()
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

    def yank_to_clipboard(self):
        try:
            path = self.navigator.current_entry.path
            pyperclip.copy(path)
            logger.info(f"Yanked '{path} to system clipboard")
            notify.show(f"Yanked to clipboard", duration=1)
        except pyperclip.PyperclipException:
            logger.exception(f"Failed to yank current path '{path}'")
            notify.show("Failed to yank: system has no clipboard", duration=2)

    def toggle_dotfiles(self):
        self.model.show_hidden_files = not self.model.show_hidden_files
        if self.model.show_hidden_files:
            message = 'show dotfiles'
        else:
            message = 'hide dotfiles'
        notify.show(message, duration=0.7)


class NormalControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)
        self.ACTION_TO_CALL.update({
            NormalAction.go_to_parent: self.go_to_parent,
            NormalAction.go_to_home: self.go_to_home,
            NormalAction.go_to_root: self.go_to_root,
            NormalAction.go_to_previous: self.go_to_previous,
            NormalAction.go_to_next: self.go_to_next,
            NormalAction.assign_mode: self.enter_assign_mode,
            NormalAction.edit_mode: self.enter_edit_mode,
        })

    def handle_key_individually(self, key):
        if hook.is_hook(key, self.model.current_entry):
            hook.trigger_hook(key, self.model.current_entry)
        elif self.navigator.is_navigation_key(key):
            self.go_to_key(key)
            return True

    def go_to_key(self, key: str):
        self.navigator.visit_child(key)
        self.clear_filter()

    def go_to_parent(self):
        self.navigator.visit_parent()
        self.clear_filter()

    def go_to_home(self):
        self.navigator.visit_path(environment.home)
        self.clear_filter()

    def go_to_root(self):
        self.navigator.visit_path('/')
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

    def enter_assign_mode(self):
        viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_ENTRY
        self.list.render(self.list_size, True)

    def enter_edit_mode(self):
        viewmodel.global_mode.mode = Mode.EDIT


class AssignControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)
        self.entry_for_assignment = None
        self.ACTION_TO_CALL.update({
            AssignAction.abort: self.abort_assign_mode,
            AssignAction.select_next: self.select_next,
            AssignAction.select_previous: self.select_previous,
        })

    def handle_key_individually(self, key):
        if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY and self.navigator.is_navigation_key(key):
            self.keypress_choose_entry(key)
            return True
        elif viewmodel.global_mode == Mode.ASSIGN_CHOOSE_KEY and key_module.is_navigation_key(key):
            self.keypress_choose_key(key)
            return True

    def abort_assign_mode(self):
        viewmodel.global_mode.mode = Mode.NORMAL
        self.list.render(self.list_size, True)

    def select_next(self):
        try:
            self.list.set_focus(self.list.focus_position + 1, coming_from='below')
        except IndexError:
            pass

    def select_previous(self):
        try:
            self.list.set_focus(self.list.focus_position - 1, coming_from='above')
        except IndexError:
            pass

    def exit(self):
        if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.select_widget(self.list.walker[self.list.focus_position])

    def choose(self, key: str):
        if viewmodel.global_mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.keypress_choose_entry(key)
        elif viewmodel.global_mode == Mode.ASSIGN_CHOOSE_KEY:
            self.keypress_choose_key(key)

    def keypress_choose_entry(self, key: str):
        if key in key_module.get_all_keys():
            self.select_entry_with_key(key)
        elif key == 'enter':
            self.select_widget(self.list.walker[self.list.focus_position])
        else:
            return key

    def keypress_choose_key(self, key: str):
        if key in key_module.get_all_keys():
            self.assign_key(key)
        else:
            return key

    def select_entry_with_key(self, key):
        match = self.navigator.current_entry.get_child_for_key(key_module.Key(key))
        if match:
            results = [x for x in self.list.walker if x.base_widget.entry == match]
            if len(results) > 0:
                chosen_widget = results[0]
                self.select_widget(chosen_widget)
            else:
                # entry is not displayed, probably filtered
                self.list.walker.append(self.list.create_list_entry(match))
                self.select_entry_with_key(key)

    def select_widget(self, entry_widget):
        self.list.walker.set_focus(self.list.walker.index(entry_widget))
        self.entry_for_assignment = self.list.walker[self.list.walker.focus].base_widget.entry
        viewmodel.global_mode.mode = Mode.ASSIGN_CHOOSE_KEY

    def assign_key(self, key: str):
        if key in key_module.get_all_keys():
            self.navigator.assign_key(key_module.Key(key), self.entry_for_assignment.path)
            self.abort_assign_mode()
            self.list.on_entries_changed(self.model)


class EditControl(Control):

    def __init__(self, frame: 'MainFrame'):
        super().__init__(frame)
