import logging

import urwid
from urwid import AttrSpec, ListBox

from core import key as key_module
from core.entry import Entry, EntryType
from core.navigator import Navigator
from ui import theme, graphics
from ui.viewmodel import ViewModel, Mode
from util import keymap
from util.keymap import Action

logger = logging.getLogger(__name__)


class List(ListBox):

    def __init__(self):
        self.walker = urwid.SimpleFocusListWalker([])
        super().__init__(self.walker)

    def scroll(self, offset: int, coming_from=None, valign=None):
        try:
            index = self.focus_position + offset
            self.set_focus(index, coming_from=coming_from)
            if valign:
                self.set_focus_valign(valign)
        except IndexError:
            pass

    def keypress(self, size, key):
        if keymap.matches(Action.SCROLL_PAGE_DOWN, key):
            self.scroll_page_down(size)
        elif keymap.matches(Action.SCROLL_PAGE_UP, key):
            self.scroll_page_up(size)
        elif keymap.matches(Action.SCROLL_HALF_PAGE_DOWN, key):
            self.scroll_half_page_down(size)
        elif keymap.matches(Action.SCROLL_HALF_PAGE_UP, key):
            self.scroll_half_page_up(size)
        else:
            return key

    def scroll_page_down(self, size):
        _, max_row = size
        self._scroll_down(size, max_row)

    def scroll_page_up(self, size):
        _, max_row = size
        self._scroll_up(size, max_row)

    def scroll_half_page_down(self, size):
        _, max_row = size
        self._scroll_down(size, max_row // 2)

    def scroll_half_page_up(self, size):
        _, max_row = size
        self._scroll_up(size, max_row // 2)

    def _scroll_down(self, size, amount):
        middle, top, bottom = self.calculate_visible(size)
        relative_position = (len(top[1]) / (len(top[1]) + 1 + len(bottom[1]))) * 100
        max_line = len(self.body) - 1
        new_focus = min(self.focus_position + amount, max_line)
        self.set_focus(new_focus)
        self.set_focus_valign(('relative', relative_position))

    def _scroll_up(self, size, amount):
        middle, top, bottom = self.calculate_visible(size)
        relative_position = ((len(top[1]) + 1) / (len(top[1]) + 1 + len(bottom[1]))) * 100
        new_focus = max(self.focus_position - amount, 0)
        self.set_focus(new_focus)
        self.set_focus_valign(('relative', relative_position))


class EntryList(List):

    def __init__(self, mainpane, model: ViewModel, navigator: Navigator):
        super().__init__()
        self.mainpane = mainpane
        self.box = None
        self.model = model
        self.navigator = navigator
        self.entry_for_assignment = None
        self.model.register(self)

    def on_update(self):
        with graphics.DRAW_LOCK:
            self.walker.clear()
            self.walker.extend(
                [self.create_list_entry(entry) for entry in self.model.entries])
            self.walker.set_focus(0)

    def create_list_entry(self, entry):
        return urwid.Padding(ListEntry(entry, self.model), left=4)

    def keypress(self, size, key):
        mode = self.model.mode
        if keymap.matches(Action.TOGGLE_DOTFILES, key):
            self.toggle_hidden_files()
            return
        elif key == 'esc' and (mode == Mode.ASSIGN_CHOOSE_KEY or mode == Mode.ASSIGN_CHOOSE_ENTRY):
            self.exit_assign_mode(size)
            return
        elif mode == Mode.ASSIGN_CHOOSE_ENTRY:
            key = self.keypress_choose_entry(size, key)
        elif mode == Mode.ASSIGN_CHOOSE_KEY:
            key = self.keypress_choose_key(size, key)

        if key:
            return super().keypress(size, key)

    def toggle_hidden_files(self):
        self.model.show_hidden_files = not self.model.show_hidden_files
        if self.model.show_hidden_files:
            message = 'show dotfiles'
        else:
            message = 'hide dotfiles'
        graphics.notify(message, duration=0.7)

    def keypress_choose_entry(self, size, key):
        if key in key_module.get_all_keys():
            self.select_entry_with_key(key)
        elif key == 'ctrl n':
            self.selection_down()
        elif key == 'ctrl p':
            self.selection_up()
        elif key == 'enter':
            self.select_widget(self.walker[self.focus_position])
        else:
            return key

    def keypress_choose_key(self, size, key):
        if key in key_module.get_all_keys():
            self.assign_key(key, size)
        else:
            return key

    def enter_assign_mode(self, size):
        self.model.mode = Mode.ASSIGN_CHOOSE_ENTRY
        self.mainpane.update_title()
        self.render(size, True)

    def select_entry_with_key(self, key):
        match = self.navigator.current_entry.get_child_for_key(key_module.Key(key))
        if match:
            results = [x for x in self.walker if x.base_widget.entry == match]
            if len(results) > 0:
                chosen_widget = results[0]
                self.select_widget(chosen_widget)
            else:
                # entry is not displayed, probably filtered
                self.walker.append(self.create_list_entry(match))
                self.select_entry_with_key(key)

    def select_widget(self, entry_widget):
        self.walker.set_focus(self.walker.index(entry_widget))
        self.entry_for_assignment = self.walker[self.walker.focus].base_widget.entry
        self.model.mode = Mode.ASSIGN_CHOOSE_KEY
        self.mainpane.update_title()

    def exit_assign_mode(self, size):
        self.model.mode = Mode.NORMAL
        self.mainpane.update_title()
        self.render(size, True)

    def assign_key(self, key: str, size):
        if key in key_module.get_all_keys():
            self.navigator.assign_key(key_module.Key(key), self.entry_for_assignment.path)
            self.exit_assign_mode(size)
            self.on_update()

    def selection_up(self):
        try:
            self.set_focus(self.focus_position - 1, coming_from='above')
        except IndexError:
            pass

    def selection_down(self):
        try:
            self.set_focus(self.focus_position + 1, coming_from='below')
        except IndexError:
            pass


class ListEntry(urwid.Text):

    def __init__(self, entry: Entry, model: ViewModel):
        self.entry = entry
        self.model = model
        self.color = compute_color(entry)
        # TODO setup spacing relative to available space
        # spacing = min((1 + (self.rows() // 25)), 3)
        spacing = 4
        spacing_right = ' ' * spacing
        key = " " if entry.key.value == "" else entry.key.value
        self.display = key + spacing_right + entry.name
        super().__init__((self.color, self.display), wrap='clip')

    def render(self, size, focus=False):
        if focus and self.model.mode != Mode.NORMAL:
            color = AttrSpec(self.color.foreground + ',standout', self.color.background, colors=16)
        else:
            color = self.color
        self.set_text((color, self.display))
        return super().render(size, focus=focus)


def compute_color(entry: Entry) -> AttrSpec:
    rating = entry.rating
    if entry._parent.unexplored:
        rating = 0.5
    bold = False
    unimportant = False
    if not entry.readable:
        color = theme.forbidden
    elif rating < 0.05:
        color = theme.unused
    else:
        if rating >= 0.6:
            bold = True
        elif rating < 0.2:
            unimportant = True
        if entry.type == EntryType.DIRECTORY:
            color = theme.directory
        elif entry.type == EntryType.SYMLINK:
            color = theme.symlink
        elif entry.executable:
            color = theme.executable
        else:
            color = theme.file
    if unimportant:
        color = theme.unimportant[color]
    if bold:
        color = color + ',bold'
    return AttrSpec(color, '', colors=16)
