import urwid
from pygments import token
from sodalite.ui import viewmodel
from sodalite.ui.viewmodel import Topic, Mode

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

navigate_mode = 'navigate_mode'
assign_mode = 'assign_mode'
operate_mode = 'operate_mode'

palette = (
    ('underline', 'underline', ''),
    (bold, 'bold', ''),
    (reverse, 'standout', ''),

    (navigate_mode, urwid.DEFAULT, ''),
    (assign_mode, urwid.DARK_GREEN, ''),
    (operate_mode, urwid.DARK_RED, ''),

    # text preview highlighting
    (line_number, urwid.DARK_GRAY, ''),
    (token.Comment, urwid.DARK_GRAY, ''),
    (token.Comment.Hashbang, urwid.DARK_GRAY + ',italics', ''),
    (token.Comment.Preproc, urwid.DARK_BLUE, ''),
    (token.Comment.PreprocFile, urwid.DARK_GREEN, ''),
    (token.Comment.Single, urwid.DARK_GRAY, ''),
    (token.Generic.Emph, urwid.YELLOW, ''),
    (token.Generic.Heading, urwid.DARK_BLUE + ',bold,underline', ''),
    (token.Generic.Subheading, urwid.DARK_BLUE + ',bold', ''),
    (token.Literal.Number, urwid.LIGHT_RED, ''),
    (token.Literal.Number.Integer, urwid.LIGHT_RED, ''),
    (token.Literal.Number.Float, urwid.LIGHT_RED, ''),
    (token.Literal.String, urwid.DARK_GREEN, ''),
    (token.Literal.String.Backtick, urwid.DARK_GREEN + ',italics', ''),
    (token.Literal.String.Escape, urwid.LIGHT_MAGENTA, ''),
    (token.Literal.String.Interpol, urwid.LIGHT_CYAN, ''),
    (token.Literal.String.Single, urwid.DARK_GREEN, ''),
    (token.Literal.String.Doc, urwid.DARK_GREEN, ''),
    (token.Literal.String.Double, urwid.LIGHT_GREEN, ''),
    (token.Keyword, urwid.DARK_BLUE, ''),
    (token.Keyword.Reserved, urwid.LIGHT_BLUE, ''),
    (token.Keyword.Declaration, urwid.YELLOW, ''),
    (token.Keyword.Constant, urwid.YELLOW, ''),
    (token.Keyword.Namespace, urwid.DARK_BLUE, ''),
    (token.Keyword.Type, urwid.BROWN, ''),
    (token.Name, urwid.WHITE, ''),
    (token.Name.Attribute, urwid.DARK_CYAN, ''),
    (token.Name.Builtin, urwid.LIGHT_BLUE, ''),
    (token.Name.Builtin.Pseudo, urwid.YELLOW, ''),
    (token.Name.Class, '', ''),
    (token.Name.Decorator, urwid.DARK_BLUE, ''),
    (token.Name.Function, ',bold', ''),
    (token.Name.Namespace, '', ''),
    (token.Name.Variable, urwid.DARK_CYAN, ''),
    (token.Name.Tag, urwid.WHITE, ''),
    (token.Operator, urwid.WHITE, ''),
    (token.Operator.Word, urwid.DARK_GREEN, ''),
    (token.Punctuation, urwid.WHITE, ''),
    (token.Text, urwid.WHITE, ''),
)


class DynamicAttrMap(urwid.AttrMap):

    def __init__(self, w):
        super().__init__(w, navigate_mode)
        viewmodel.global_mode.register(self.update_colors, topic=Topic.MODE)

    def update_colors(self, model):
        if viewmodel.global_mode == Mode.NAVIGATE:
            attr = navigate_mode
        elif viewmodel.global_mode in (Mode.ASSIGN_CHOOSE_ENTRY, Mode.ASSIGN_CHOOSE_KEY):
            attr = assign_mode
        elif viewmodel.global_mode == Mode.OPERATE:
            attr = operate_mode
        else:
            raise ValueError
        self.set_attr_map({None: attr})
