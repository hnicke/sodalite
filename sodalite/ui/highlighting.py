import logging
from pathlib import Path
from typing import Pattern, Generator

import pygments
from pygments import lexers, token
from pygments.lexers.shell import BashLexer

from sodalite.core.entry import Entry
from sodalite.ui import theme

logger = logging.getLogger(__name__)


class HighlightedLine:
    def __init__(self, content, linenumber):
        self.content = self.bold_headings(content)
        self.raw_content = ''.join([word for attr, word in self.content])
        self.linenumber = linenumber
        formatted_linenumber = [(theme.line_number, u'{:>2} '.format(linenumber))]
        self.numbered_content = [formatted_linenumber] + content

    def bold_headings(self, content):
        heading = None
        new_content = []
        for attr, word in content:
            if attr is token.Generic.Heading or attr is token.Generic.Subheading:
                heading = attr
            if heading:
                attr = heading
            new_content.append((attr, word))
        return new_content

    def matches(self, pattern: Pattern):
        return not pattern.pattern or pattern.search(self.raw_content)

    def __str__(self):
        return f"[{self.linenumber}: {self.content}]"


def compute_highlighting(entry: Entry) -> Generator[HighlightedLine, None, None]:
    lexer = find_lexer(entry.path, entry.content)
    logger.info("Using {} for highlighting".format(type(lexer).__name__))
    content = entry.content.replace('\t', "    ")
    tokens = list(lexer.get_tokens(content))
    return line_per_line(tokens)


def find_lexer(file: Path, content: str):
    try:
        if file.name in ('.gitignore', '.dockerignore'):
            lexer = BashLexer()
        else:
            lexer = lexers.guess_lexer_for_filename(str(file), content, stripnl=False,
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


def line_per_line(tokens) -> Generator[HighlightedLine, None, None]:
    line = []
    pos = 0
    for attr, _token in tokens:
        while '\n' in _token:
            index = _token.index('\n')
            begin = _token[:index]
            _token = _token[index + 1:]
            if begin:
                line.append((attr, begin))
            pos += 1
            yield HighlightedLine(line, pos)
            line = []
        if _token:
            line.append((attr, _token))
    if len(line) >= 1:
        yield HighlightedLine(line, pos)
