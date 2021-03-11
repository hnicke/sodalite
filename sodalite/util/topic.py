from blinker import Signal

entry = Signal('entry')
"""args: Entry"""

entry_list = Signal('entry-list')
"""args: list[Entry]"""

filesystem = Signal('filesystem')
"""args: -"""

filtered_file_content = Signal('filtered-file-content')
"""args: list[HighlightedLine]"""

mode = Signal('mode')
"""args: Mode"""
