import urwid
from pygments import token

file = urwid.WHITE
file_unimportant = urwid.LIGHT_GRAY
directory = urwid.LIGHT_BLUE
directory_unimportant = urwid.DARK_BLUE
symlink = urwid.LIGHT_CYAN
symlink_unimportant = urwid.DARK_CYAN
executable = urwid.LIGHT_GREEN
executable_unimportant = urwid.DARK_GREEN

reverse = 'reverse'
bold = 'bold'
line_number = 'line_number'

unimportant = {
    file: file_unimportant,
    directory: directory_unimportant,
    symlink: symlink_unimportant,
    executable: executable_unimportant
}
unused = urwid.DARK_GRAY
forbidden = urwid.LIGHT_RED

palette = (
    ('underline', 'underline', ''),
    (bold, 'bold', ''),
    (reverse, 'standout', ''),

    # text preview highlighting
    (line_number, urwid.DARK_GRAY, ''),
    (token.Comment, urwid.DARK_GRAY, ''),
    (token.Comment.Single, urwid.DARK_GRAY, ''),
    (token.Comment.Hashbang, urwid.DARK_GRAY, ''),
    (token.Literal.Number, urwid.DARK_RED, ''),
    (token.Literal.Number.Integer, urwid.DARK_RED, ''),
    (token.Literal.Number.Float, urwid.DARK_RED, ''),
    (token.Literal.String, urwid.LIGHT_RED, ''),
    (token.Literal.String.Doc, urwid.DARK_GREEN, ''),
    (token.Literal.String.Double, urwid.LIGHT_GREEN, ''),
    (token.Keyword, urwid.DARK_BLUE, ''),
    (token.Keyword.Namespace, urwid.DARK_BLUE, ''),
    (token.Name, urwid.WHITE, ''),
    (token.Name.Builtin, urwid.DARK_CYAN, ''),
    (token.Name.Builtin.Pseudo, urwid.YELLOW, ''),
    (token.Name.Class, urwid.YELLOW, ''),
    (token.Name.Function, urwid.LIGHT_BLUE, ''),
    (token.Name.Namespace, '', ''),
    (token.Name.Variable, urwid.DARK_CYAN, ''),
    (token.Operator, urwid.WHITE, ''),
    (token.Operator.Word, urwid.DARK_GREEN, ''),
    (token.Punctuation, urwid.WHITE, ''),
    (token.Text, urwid.WHITE, ''),
)
