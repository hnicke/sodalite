import logging
import os

import pyperclip
import urwid
from urwid import AttrSpec

import core.key as key_module
from core.entry import Entry, EntryType
from old_ui.viewmodel import ViewModel, Mode
from ui import theme, app
from ui.filter import Filter
from util import environment

logger = logging.getLogger(__name__)


class FileList(urwid.WidgetWrap):

    def __init__(self, model: ViewModel):
        self.model = model
        self.navigator = self.model.navigator
        self.walker = urwid.SimpleFocusListWalker([])
        self.file_list = urwid.ListBox(self.walker)
        self.frame = urwid.Frame(self.file_list)
        self.box = urwid.LineBox(self.frame, title_align='left')
        self.box.title_widget.set_layout('right', 'clip')
        self.model.register(self)
        self.entry_for_assignment = None
        super().__init__(self.box)

    def on_update(self):
        self.walker.clear()
        self.walker.extend(
            [self.create_list_entry(entry) for entry in self.model.filtered_children])
        self.walker.set_focus(0)
        self.update_title()

    def create_list_entry(self, entry):
        return urwid.Padding(ListEntry(entry, self.model), left=4)

    def update_title(self):
        mode = self.model.mode
        if mode == Mode.NORMAL:
            self.set_title_to_cwd()
        elif mode == Mode.ASSIGN_CHOOSE_ENTRY:
            self.box.set_title("assign key: choose entry")
        elif mode == Mode.ASSIGN_CHOOSE_KEY:
            self.box.set_title("assign key: choose new key")

    def set_title_to_cwd(self):
        cwd = self.model.current_entry.path
        if cwd.startswith(environment.home):
            cwd = "~" + cwd[len(environment.home):]
        self.box.set_title(cwd)

    def keypress(self, size, key):
        maxcol, maxrow = size
        try:
            if key == '/':
                if not self.frame.footer:
                    self.frame.footer = Filter(self.model, self.frame)
                self.frame.focus_position = 'footer'
            elif key == 'ctrl f':
                self.scroll(maxrow, valign='top')
            elif key == 'ctrl b':
                self.scroll(-maxrow, valign='top')
            elif key == 'ctrl d':
                self.scroll(maxrow // 2, valign='top')
            elif key == 'ctrl u':
                self.scroll(-(maxrow // 2), valign='top')

            elif self.model.mode == Mode.NORMAL:
                return self.handle_normal_keypress(size, key)
            else:
                return self.handle_assign_keypress(size, key)
        except PermissionError:
            app.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "PERMISSION DENIED"))
            return key
        except FileNotFoundError:
            app.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "FILE NOT FOUND"))
            return key

    def handle_normal_keypress(self, size, key):
        if key == '.':
            self.navigator.visit_parent()
            self.clear_filter()
        elif key == '~' or key == '`':
            self.navigator.visit_path(environment.home)
            self.clear_filter()
        elif key == 'backspace':  # also matches ctrl h
            self.navigator.visit_previous()
            self.clear_filter()
        elif key == 'ctrl l':
            self.navigator.visit_next()
            self.clear_filter()
        elif self.navigator.is_navigation_key(key):
            self.navigator.visit_child(key)
            self.clear_filter()
        elif key == 'enter':
            append_to_cwd_pipe(self.navigator.history.cwd())
            raise urwid.ExitMainLoop()
        elif key == 'ctrl y':
            pyperclip.copy(self.model.current_entry.path)
        elif key == '=':
            self.enter_assign_mode(size)
        else:
            return key

    def clear_filter(self):
        if self.frame.footer:
            self.frame.footer.clear_filter()

    def handle_assign_keypress(self, size, key):
        if key == 'esc':
            self.exit_assign_mode(size)
        elif self.model.mode == Mode.ASSIGN_CHOOSE_ENTRY:
            if key in key_module.get_all_keys():
                self.select_entry_with_key(key)
            elif key == 'ctrl n':
                self.scroll(1, coming_from='above')
            elif key == 'ctrl p':
                self.scroll(-1, coming_from='below')
            elif key == 'enter':
                self.select_widget(self.walker[self.file_list.focus_position])
            else:
                return key
        elif self.model.mode == Mode.ASSIGN_CHOOSE_KEY:
            if key in key_module.get_all_keys():
                self.assign_key(key, size)
            else:
                return key
        return None

    def scroll(self, offset: int, coming_from=None, valign=None):
        try:
            index = self.file_list.focus_position + offset
            self.file_list.set_focus(index, coming_from=coming_from)
            if valign:
                self.file_list.set_focus_valign(valign)
        except IndexError:
            pass

    def enter_assign_mode(self, size):
        self.model.mode = Mode.ASSIGN_CHOOSE_ENTRY
        self.update_title()
        self.file_list.render(size, True)

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
        self.update_title()

    def exit_assign_mode(self, size):
        self.model.mode = Mode.NORMAL
        self.update_title()
        self.file_list.render(size, True)

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


# TODO move somewhere else
def append_to_cwd_pipe(cwd: str):
    """Before exiting, this needs to be called once, or the wrapping script won't stop
    :param cwd: a path, will get written to output pipe if pipe exists
    """
    pipe = environment.cwd_pipe
    if pipe is not None and os.path.exists(pipe):
        logger.info("Writing '{}' to cwd_pipe '{}'".format(cwd, environment.cwd_pipe))
        with open(environment.cwd_pipe, 'w') as p:
            p.write(cwd)
            p.close()
