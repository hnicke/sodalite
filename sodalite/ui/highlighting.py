import logging
from typing import List, Pattern

import pygments
from pygments import lexers, token
from pygments.lexers.shell import BashLexer

from core.entry import Entry
from ui import theme

logger = logging.getLogger(__name__)


class HighlightedLine:
    def __init__(self, content, linenumber):
        self.content = self.bold_headings(content)
        self.raw_content = ''.join([word for attr, word in self.content])
        self.linenumber = linenumber
        formatted_linenumber = [(theme.line_number, u'{:>2} '.format(linenumber))]
        self.numbered_content = [formatted_linenumber] + content

    def bold_headings(self, content):
        heading = False
        new_content = []
        for attr, word in content:
            if attr is token.Generic.Heading or attr is token.Generic.Subheading:
                heading = True
            if heading and attr in token.Text:
                attr = 'bold'
            new_content.append((attr, word))
        return new_content

    def matches(self, pattern: Pattern):
        return not pattern.pattern or pattern.search(self.raw_content)

    def __str__(self):
        return f"[{self.linenumber}: {self.content}]"


def compute_highlighting(entry: Entry) -> List[HighlightedLine]:
    lexer = find_lexer(entry.path, entry.content)
    logger.info("Using {} for highlighting".format(type(lexer).__name__))
    content = entry.content.replace('\t', "    ")
    tokens = list(lexer.get_tokens(content))
    return line_per_line(tokens)


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


def line_per_line(tokens) -> List[HighlightedLine]:
    line = []
    pos = 0
    for attr, token in tokens:
        while '\n' in token:

            index = token.index('\n')
            begin = token[:index]
            token = token[index + 1:]
            if begin:
                line.append((attr, begin))
            pos += 1
            yield HighlightedLine(line, pos)
            line = []
        if token:
            line.append((attr, token))
    if len(line) >= 1:
        yield HighlightedLine(line, pos)
