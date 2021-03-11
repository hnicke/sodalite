import urwid
from urwid import Frame

from sodalite.ui.viewmodel import ViewModel


class Filter(urwid.Edit):
    def __init__(self, model: ViewModel, parent: Frame):
        self.model = model
        self.parent = parent
        self.cursor_col = 1
        self._active = False
        super().__init__(caption=u'/')
        urwid.connect_signal(self, 'postchange', self.update_filter)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, active):
        if active:
            focus = 'footer'
            if self.parent.footer is not self:
                self.parent.footer = self
        else:
            focus = 'body'
        self.parent.focus_part = focus
        self._active = active
        self._invalidate()

    def keypress(self, size, key):
        if key == 'esc':
            self.hide()
        elif key == 'enter':
            self.active = False
        else:
            super().keypress(size, key)

    def update_filter(self, *args, **keywords):
        self.model.filter_pattern = self.edit_text

    def hide(self):
        self.set_edit_text('')
        self.active = False
        self.parent.footer = None

    def get_cursor_coords(self, size):
        if self.active:
            return super().get_cursor_coords(size)
