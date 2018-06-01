import pygments
from pygments import lexers
from pygments.lexers.shell import BashLexer
from urwid import Text, ListBox, SimpleListWalker

from ui import theme


class FilePreview(ListBox):
    def __init__(self, model):
        walker = SimpleListWalker([])
        super().__init__(walker)
        self.model = model
        self.model.register(self)

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
            tokens = list(lexer.get_tokens(self.model.file_content))
            tokens_with_line_numbers = inject_linenumbers(tokens)
            self.body.clear()
            self.body.extend([Text(line) for line in tokens_with_line_numbers])


def inject_linenumbers(tokens):
    splitted = [[]]
    pos = 0
    splitted[pos].append((theme.line_number, u"{:>2} ".format(pos + 1)))
    for format, token in tokens:
        while '\n' in token:
            index = token.index('\n')
            begin = token[:index]
            token = token[index + 1:]
            if begin:
                splitted[pos].append((format, begin))
            pos += 1
            splitted.append([])
            splitted[pos].append((theme.line_number, u'{:>2} '.format(pos + 1)))
        if token:
            splitted[pos].append((format, token))
    del splitted[pos]
    return splitted
