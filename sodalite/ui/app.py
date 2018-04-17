import urwid

from ui.filelist import FileList


def run():
    file_list = FileList()
    frame = urwid.Frame(file_list)
    loop = urwid.MainLoop(frame)
    loop.run()
