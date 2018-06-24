import logging

import pygments
from pygments import lexers, token
from pygments.lexers.shell import BashLexer
from urwid import Text

from ui import theme, graphics
from ui.entrylist import List

logger = logging.getLogger(__name__)


class FilePreview(List):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.model.register(self)

    def on_update(self):
        with graphics.DRAW_LOCK:
            self.body.clear()
            content = self.model.file_content
            if content:
                lexer = find_lexer(self.model.current_entry.path, content)
                logger.info("Viewing file content - using {} for highlighting".format(type(lexer).__name__))
                tokens = list(lexer.get_tokens(self.model.file_content))
                # tabs are not rendered correctly, replace them with spaces
                tokens = replace_tabs(tokens)
                self.body.extend([Text(line) for line in bold_headings(inject_linenumbers(tokens))])
                self.focus_position = 0


def replace_tabs(tokens):
    return [(attr, line.replace("\t", "    ")) for attr, line in tokens]


def find_lexer(filename: str, content: str):
    try:
        lexer = lexers.guess_lexer_for_filename(filename, content, stripnl=False,
                                                ensurenl=False)
        logger.debug('Detected lexer by filename')
    except pygments.util.ClassNotFound:
        try:
            lexer = lexers.guess_lexer(content, stripnl=False, ensurenl=False)
            logger.debug('Detected lexer by file content')
        except pygments.util.ClassNotFound:
            lexer = BashLexer(stripnl=False, ensurenl=False)
            logger.debug('Using fallback lexer')
    return lexer


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
    if len(line) > 1:
        yield line


def bold_headings(lines):
    for line in lines:
        heading = False
        new_line = []
        for attr, word in line:
            if attr is token.Generic.Heading or attr is token.Generic.Subheading:
                heading = True
            if heading and attr in token.Text:
                attr = 'bold'
            new_line.append((attr, word))
        yield new_line
