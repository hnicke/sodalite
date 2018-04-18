import urwid
from urwid import Frame

from old_ui.viewmodel import ViewModel


class Filter(urwid.Edit):
    def __init__(self, model: ViewModel, parent: Frame):
        self.model = model
        self.parent = parent
        self.cursor_col = 1
        urwid.connect_signal(self, 'postchange', self.update_filter)
        super().__init__(caption=u'/')

    def keypress(self, size, key):
        if key == 'esc':
            self.clear_filter()
        elif key == 'enter':
            self.parent.focus_part = 'body'
            self._invalidate()
        else:
            super().keypress(size, key)

    def update_filter(self, *args, **keywords):
        self.model.filter(self.edit_text)

    def clear_filter(self):
        self.model.filter('')
        self.parent.footer = None

    def render(self, size, focus=False):
        # hide cursor if not editing
        canvas = super().render(size, focus=focus)
        if not focus:
            canvas = urwid.CompositeCanvas(canvas)
            canvas.cursor = None
        return canvas
