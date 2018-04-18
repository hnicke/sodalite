import os

import pyperclip
import urwid
from urwid import AttrSpec

import core.key as key_module
from core.entry import Entry, EntryType
from core.navigator import logger
from old_ui.viewmodel import ViewModel, Mode
from ui import theme, app
from util import environment


class FileList(urwid.WidgetWrap):

    def __init__(self, model: ViewModel):
        self.model = model
        self.navigator = self.model.navigator
        self.walker = urwid.SimpleFocusListWalker([])
        file_list = urwid.ListBox(self.walker)
        self.box = urwid.LineBox(file_list, title_align='left')
        self.box.title_widget.set_layout('right', 'clip')
        self.model.register(self)
        self.entry_for_assignment = None
        super().__init__(self.box)

    def on_update(self):
        self.walker.clear()
        self.walker.extend(
            [urwid.Padding(ListEntry(entry, self.model), left=4) for entry in self.model.sorted_children])
        self.walker.set_focus(0)
        self.update_title()

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
        try:
            logger.info(str(key))
            if self.model.mode == Mode.NORMAL:
                return self.handle_normal_keypress(key)
            else:
                return self.handle_assign_keypress(key)
        except PermissionError:
            app.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "PERMISSION DENIED"))
            return key
        except FileNotFoundError:
            app.notify((AttrSpec(theme.forbidden + ',bold', '', colors=16), "FILE NOT FOUND"))
            return key

    def handle_normal_keypress(self, key):
        if key == '.':
            self.navigator.visit_parent()
        elif key == '~' or key == '`':
            self.navigator.visit_path(environment.home)
        elif key == 'backspace':  # also matches ctrl h
            self.navigator.visit_previous()
        elif key == 'ctrl l':
            self.navigator.visit_next()
        elif self.navigator.is_navigation_key(key):
            self.navigator.visit_child(key)
        elif key == 'enter':
            append_to_cwd_pipe(self.navigator.history.cwd())
            raise urwid.ExitMainLoop()
        elif key == 'ctrl y':
            pyperclip.copy(self.model.current_entry.path)
        elif key == '=':
            self.enter_assign_mode()
        else:
            return key
        return None

    def handle_assign_keypress(self, key):
        if key == 'esc':
            self.exit_assign_mode()
        elif self.model.mode == Mode.ASSIGN_CHOOSE_ENTRY:
            if key in key_module.get_all_keys():
                self.select_entry(key)
            elif key == 'ctrl n':
                self.scroll(1)
            elif key == 'ctrl p':
                self.scroll(-1)
            else:
                return key
        elif self.model.mode == Mode.ASSIGN_CHOOSE_KEY:
            if key in key_module.get_all_keys():
                self.assign_key(key)
            else:
                return key
        return None

    def scroll(self, offset: int):
        try:
            self._w.base_widget.set_focus(self._w.base_widget.focus_position + offset)
        except IndexError:
            pass

    def enter_assign_mode(self):
        self.model.mode = Mode.ASSIGN_CHOOSE_ENTRY
        self.update_title()

    def select_entry(self, key):
        match = self.navigator.current_entry.get_child_for_key(key_module.Key(key))
        if match:
            self.entry_for_assignment = match
            chosen_widget = [x for x in self.walker if x.base_widget.entry == match][0]
            self._w.base_widget.focus_position = self.walker.index(chosen_widget)
            self.model.mode = Mode.ASSIGN_CHOOSE_KEY
            self.update_title()

    def exit_assign_mode(self):
        self.model.mode = Mode.NORMAL
        self.update_title()
        self.walker.set_focus(0)

    def assign_key(self, key: str):
        if key in key_module.get_all_keys():
            self.navigator.assign_key(key_module.Key(key), self.entry_for_assignment.path)
            self.exit_assign_mode()
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
