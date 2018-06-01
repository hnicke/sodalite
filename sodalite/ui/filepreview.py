import logging

import pygments
from pygments import lexers
from pygments.lexers.shell import BashLexer
from urwid import Text, ListBox, SimpleListWalker

from ui import theme

logger = logging.getLogger(__name__)


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
                                                        ensurenl=False)
                logger.debug('Detected lexer by filename')
            except pygments.util.ClassNotFound:
                try:
                    lexer = lexers.guess_lexer(content, stripnl=False, ensurenl=False)
                    logger.debug('Detected lexer by file content')
                except pygments.util.ClassNotFound:
                    lexer = BashLexer(stripnl=False, ensurenl=False)
                    logger.debug('Using fallback lexer')
            logger.info("Viewing file content - using {} for highlighting".format(type(lexer).__name__))
            tokens = list(lexer.get_tokens(self.model.file_content))
            tokens_with_line_numbers = inject_linenumbers(tokens)
            self.body.clear()
            self.body.extend([Text(line) for line in tokens_with_line_numbers])


def inject_linenumbers(tokens):
    line = []
    pos = 0
    line.append((theme.line_number, u"{:>2} ".format(pos + 1)))
    for attr, token in tokens:
        while '\n' in token:
            index = token.index('\n')
            begin = token[:index]
            token = token[index + 1:]
            if begin:
                line.append((attr, begin))
            pos += 1
            yield line
            line = [(theme.line_number, u'{:>2} '.format(pos + 1))]
        if token:
            line.append((attr, token))
