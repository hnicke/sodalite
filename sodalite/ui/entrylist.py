import logging
import os
from typing import Optional

import urwid
from urwid import AttrSpec, ListBox

from sodalite.core.entry import Entry, EntryType
from sodalite.core.navigate import Navigator
from sodalite.ui import theme, graphics, viewmodel
from sodalite.ui.viewmodel import ViewModel, Topic

logger = logging.getLogger(__name__)


class List(ListBox):

    def __init__(self) -> None:
        self.walker = urwid.SimpleFocusListWalker([])
        super().__init__(self.walker)

    def scroll(self, offset: int, coming_from=None, valign=None) -> None:
        try:
            index = self.focus_position + offset
            self.set_focus(index, coming_from=coming_from)
            if valign:
                self.set_focus_valign(valign)
        except IndexError:
            pass

    def scroll_page_down(self, size) -> None:
        _, max_row = size
        self._scroll_down(size, max_row)

    def scroll_page_up(self, size) -> None:
        _, max_row = size
        self._scroll_up(size, max_row)

    def scroll_half_page_down(self, size) -> None:
        _, max_row = size
        self._scroll_down(size, max_row // 2)

    def scroll_half_page_up(self, size) -> None:
        _, max_row = size
        self._scroll_up(size, max_row // 2)

    def _scroll_down(self, size, amount) -> None:
        middle, top, bottom = self.calculate_visible(size)
        relative_position = (len(top[1]) / (len(top[1]) + 1 + len(bottom[1]))) * 100
        max_line = len(self.body) - 1
        new_focus = min(self.focus_position + amount, max_line)
        self.set_focus(new_focus)
        self.set_focus_valign(('relative', relative_position))

    def _scroll_up(self, size, amount) -> None:
        middle, top, bottom = self.calculate_visible(size)
        relative_position = ((len(top[1]) + 1) / (len(top[1]) + 1 + len(bottom[1]))) * 100
        new_focus = max(self.focus_position - amount, 0)
        self.set_focus(new_focus)
        self.set_focus_valign(('relative', relative_position))


class CustomEdit(urwid.Edit):
    def __init__(self, text, caption):
        super().__init__(edit_text=text, caption=caption, wrap='clip')


class ListEntry(urwid.WidgetWrap):

    def __init__(self, entry: Entry, model: ViewModel):
        self.entry = entry
        self.model = model
        self.color = compute_color(entry)
        self.entry_edit = CustomEdit('', '')
        self.entry_text = urwid.Text('', wrap='clip')
        self._editing = False
        super().__init__(self.entry_text)

    def render(self, size, focus=False):
        key = " " if self.entry.key.value == "" else self.entry.key.value
        caption = "    " + key + "    "
        text = self.entry.name
        display = caption + text
        if focus and viewmodel.global_mode in viewmodel.ANY_ASSIGN_MODE:
            color = AttrSpec(self.color.foreground + ',standout', self.color.background, colors=16)
        else:
            color = self.color
        self.entry_text.set_text((color, display))
        self.entry_edit.set_caption((color, caption))
        return super().render(size, focus=focus)

    @property
    def editing(self):
        return self._editing

    @editing.setter
    def editing(self, editing: bool):
        self._editing = editing
        if editing:
            self.entry_edit.set_edit_text(self.entry.name)
            self.entry_edit.set_edit_pos(len(os.path.splitext(self.entry.name)[0]))
            self._wrapped_widget = self.entry_edit
        else:
            self._wrapped_widget = self.entry_text

    @property
    def edit_text(self) -> str:
        return self.entry_edit.edit_text

    def keypress(self, size, key):
        super().keypress(size, key)


def compute_color(entry: Entry) -> AttrSpec:
    rating = entry.rating
    if entry.parent and entry.parent.unexplored:
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


class EntryList(List):

    def __init__(self, mainpane, model: ViewModel, navigator: Navigator):
        super().__init__()
        self.mainpane = mainpane
        self.box = None
        self.model = model
        self.navigator = navigator
        self.model.register(self.on_entries_changed, topic=Topic.ENTRIES)
        self._selection: Optional[ListEntry] = None

    def on_entries_changed(self, model):
        with graphics.DRAW_LOCK:
            self.walker.clear()
            self.walker.extend(
                [self.create_list_entry(entry) for entry in model.entries])
            self.walker.set_focus(0)

    def create_list_entry(self, entry):
        return ListEntry(entry, self.model)

    def select(self, entry: Entry):
        results = [x for x in self.walker if x.base_widget.entry == entry]
        if len(results) > 0:
            chosen_widget = results[0]
        else:
            # entry is not displayed, probably filtered
            chosen_widget = self.create_list_entry(entry)
            self.walker.append(chosen_widget)
        self.selection = chosen_widget

    def select_next(self):
        try:
            self.set_focus(self.focus_position + 1, coming_from='below')
        except IndexError:
            pass

    def select_previous(self):
        try:
            self.set_focus(self.focus_position - 1, coming_from='above')
        except IndexError:
            pass

    def get_list_entry(self, entry: Entry):
        results = [x for x in self.walker if x.base_widget.entry == entry]
        if len(results) > 0:
            return results[0]

    @property
    def selection(self):
        self._selection = self.walker[self.focus_position]
        return self._selection

    @selection.setter
    def selection(self, list_entry: ListEntry):
        self.walker.set_focus(self.walker.index(list_entry))
        self._selection = list_entry
