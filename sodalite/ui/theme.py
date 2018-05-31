from pygments import token
import urwid

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
    (token.Literal.String.Doc, urwid.DARK_GREEN, ''),
    (token.Name.Namespace, '', ''),
    (token.Name.Builtin, urwid.DARK_CYAN, ''),
    (token.Text, urwid.WHITE, ''),
    (token.Operator.Word, urwid.DARK_GREEN, ''),
    (token.Name, urwid.WHITE, ''),
    (token.Punctuation, urwid.WHITE, ''),
    (token.Keyword, urwid.LIGHT_BLUE, ''),
    (token.Name.Function, urwid.LIGHT_BLUE, ''),
    (token.Name.Class, urwid.YELLOW, ''),
    (token.Keyword.Namespace, urwid.DARK_BLUE, ''),
    (token.Name.Builtin.Pseudo, urwid.YELLOW, ''),
    (token.Operator, urwid.WHITE, ''),
    (token.Literal.Number.Integer, urwid.DARK_RED, ''),
    (token.Literal.Number.Float, urwid.DARK_RED, ''),
    (token.Literal.String, urwid.LIGHT_RED, ''),
    (token.Literal.String.Double, urwid.LIGHT_GREEN, ''),
)
