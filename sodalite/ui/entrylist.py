import urwid
from urwid import AttrSpec, ListBox

from core import key as key_module
from core.entry import Entry, EntryType
from ui import theme, app
from ui.viewmodel import ViewModel, Mode


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

    def render(self, size, focus=False):
        tes = super().render(size, focus=focus)
        return tes

    def scroll_page_down(self, size):
        maxrow, _ = size
        self._scroll_down(size, maxrow)

    def scroll_page_up(self, size):
        maxrow, _ = size
        self._scroll_up(size, maxrow)

    def scroll_half_page_down(self, size):
        maxrow, _ = size
        self._scroll_down(size, maxrow // 2)

    def scroll_half_page_up(self, size):
        maxrow, _ = size
        self._scroll_up(size, maxrow // 2)

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


class EntryList(List):

    def __init__(self, mainpane, model, navigator):
        super().__init__()
        self.mainpane = mainpane
        self.box = None
        self.model = model
        self.navigator = navigator
        self.entry_for_assignment = None
        self.model.register(self)

    def on_update(self):
        with app.DRAW_LOCK:
            self.walker.clear()
            self.walker.extend(
                [self.create_list_entry(entry) for entry in self.model.filtered_children])
            self.walker.set_focus(0)

    def create_list_entry(self, entry):
        return urwid.Padding(ListEntry(entry, self.model), left=4)

    def handle_assign_keypress(self, size, key):
        if key == 'esc':
            self.exit_assign_mode(size)
        elif self.model.mode == Mode.ASSIGN_CHOOSE_ENTRY:
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
        elif self.model.mode == Mode.ASSIGN_CHOOSE_KEY:
            if key in key_module.get_all_keys():
                self.assign_key(key, size)
            else:
                return key
        return None

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
    bold = False
    unimportant = False
    if not entry.readable:
        color = theme.forbidden
    elif entry.frequency < 2:
        color = theme.unused
    else:
        if entry.frequency >= 10:
            bold = True
        elif entry.frequency < 4:
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
