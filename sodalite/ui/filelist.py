import os

import urwid

from core.entry import Entry
from core.navigator import Navigator, logger
from old_ui.viewmodel import ViewModel
from util import environment


class FileList(urwid.WidgetWrap):

    def __init__(self):
        self.navigator = Navigator()
        self.data = ViewModel(self.navigator)
        self.walker = urwid.SimpleFocusListWalker([])
        file_list = urwid.ListBox(self.walker)
        self.box = urwid.LineBox(file_list, title_align='left')
        self.data.register(self)
        super().__init__(self.box)

    def on_update(self):
        self.walker.clear()
        self.walker.extend([ListEntry(x) for x in self.data.sorted_children])
        self.walker.set_focus(0)
        self.box.set_title(self.data.current_entry.path)

    def keypress(self, size, key):
        logger.info(str(key))
        if key == '.':
            self.navigator.visit_parent()
        elif key == 'backspace':  # also matches ctrl h
            self.navigator.visit_previous()
        elif key == 'ctrl l':  # also matches ctrl h
            self.navigator.visit_next()
        elif self.navigator.is_navigation_key(key):
            self.navigator.visit_child(key)
        elif key == 'enter':
            append_to_cwd_pipe(self.navigator.history.cwd())

            raise urwid.ExitMainLoop()
        else:
            return key
        return None


class ListEntry(urwid.WidgetWrap):

    def __init__(self, entry: Entry):
        entry_text = urwid.Text(entry.name)
        super().__init__(entry_text)
        # TODO setup spacing relative to available space
        # spacing = min((1 + (self.rows() // 25)), 3)
        spacing = 4
        spacing_left = ' ' * (spacing - 1)
        spacing_right = ' ' * spacing
        key = " " if entry.key.value == "" else entry.key.value
        display = spacing_left + key + spacing_right + entry.name
        self._w.set_text(display)


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
