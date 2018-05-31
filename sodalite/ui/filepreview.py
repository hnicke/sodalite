import pygments
import urwid
from pygments import lexers
from pygments.lexers.shell import BashLexer
from urwid import Text

from ui import theme
from ui.viewmodel import ViewModel


class LineWalker(urwid.ListWalker):
    def __init__(self, model: ViewModel):
        self.model = model
        self.model.register(self)
        self.lines = []
        self.focus = 0

    def set_focus(self, pos):
        self.focus = pos

    def get_focus(self):
        return self.get_at_pos(self.focus)

    def get_prev(self, start_from):
        return self.get_at_pos(start_from - 1)

    def get_next(self, start_from):
        return self.get_at_pos(start_from + 1)

    def get_at_pos(self, pos):
        if pos < 0 or pos >= len(self.lines):
            return None, None
        else:
            return self.lines[pos], pos

    def on_update(self):
        content = self.model.file_content
        self.lines = []
        if content:
            try:
                lexer = lexers.guess_lexer_for_filename(self.model.current_entry.path, content, stripnl=False,
                                                        stripall=False, ensurenl=False, tabsize=0)
            except pygments.util.ClassNotFound:
                try:
                    lexer = lexers.guess_lexer(content, stripnl=False, stripall=False, ensurenl=False, tabsize=0)
                except pygments.util.ClassNotFound:
                    lexer = BashLexer(stripnl=False, stripall=False, ensurenl=False, tabsize=0)
            tokens = lexer.get_tokens(self.model.file_content)
            splitted_tokens = split_tokens(tokens)
            for i, line in enumerate(splitted_tokens):
                line = [(theme.line_number, u'{:>2} '.format(i + 1))] + line
                self.lines.append(Text(line))


def split_tokens(tokens):
    splitted_tokens = [[]]
    tmp = []

    pos = 0
    for (format, token) in tokens:
        tmp.append((format, token))
        while token.endswith('\n'):
            token = token[:-1]
            pos += 1
            splitted_tokens.append([])

    # for (format, token) in tmp:
    #     for split in token.split('\n'):
    #         tmp2.append((format, split))


    return splitted_tokens
#
#
# return splitted_tokens
# splitted_tokens = [[]]
# pointer = 0
# for (format, word) in tokens:
#     if word.startswith('\n'):
#         word = word.replace('\n', '', 1)
#     for piece in word.split('\n'):
#         if piece == '':
#             pointer = pointer + 1
#             splitted_tokens.append([])
#         else:
#             splitted_tokens[pointer].append((format, piece))
# if not splitted_tokens[len(splitted_tokens) - 1]:
#     del splitted_tokens[len(splitted_tokens) - 1]
# return splitted_tokens


class FilePreview(urwid.ListBox):
    def __init__(self, model):
        super().__init__(LineWalker(model))
