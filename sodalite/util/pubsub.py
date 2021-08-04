from typing import TYPE_CHECKING, Callable, Optional

from blinker import Signal

if TYPE_CHECKING:
    from sodalite.core.entry import Entry
    from sodalite.ui.viewmodel import Mode
    from sodalite.ui.highlighting import HighlightedLine


class MemorySignal(Signal):  # type: ignore
    """
    A signal that fires the last sent signal when a receiver connects
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.latest_data: Optional[object] = None

    def send(self, o: Optional[object] = None, *args: object, **kwargs: object) -> None:
        super().send(o, *args, **kwargs)
        if o is not None:
            self.latest_data = o

    def connect(self, callback: Callable, *args: object, **kwargs: object) -> None:  # type: ignore
        super().connect(callback, *args, **kwargs)
        if self.latest_data is not None:
            callback(self.latest_data)


_entry_signal = MemorySignal('entry')
_entry_list_signal = MemorySignal('entry-list')
_filesystem_signal = MemorySignal('filesystem')
_filtered_file_content_signal = MemorySignal('filtered-file-content')
_mode_signal = MemorySignal('mode')


def entry_connect(callback: Callable[['Entry'], None]) -> None:
    _entry_signal.connect(callback)


def entry_send(entry: 'Entry') -> None:
    _entry_signal.send(entry)


def entry_list_connect(callback: Callable[[list['Entry']], None]) -> None:
    _entry_list_signal.connect(callback)


def entry_list_send(entries: list['Entry']) -> None:
    _entry_list_signal.send(entries)


def filesystem_connect(callback: Callable[[], None]) -> None:
    _filesystem_signal.connect(callback)


def filesystem_send() -> None:
    _filesystem_signal.send()


def filtered_file_content_connect(callback: Callable[[list['HighlightedLine']], None]) -> None:
    _filtered_file_content_signal.connect(callback)


def filtered_file_content_send(content: list['HighlightedLine']) -> None:
    _filtered_file_content_signal.send(content)


def mode_connect(callback: Callable[['Mode'], None]) -> None:
    _mode_signal.connect(callback)


def mode_send(mode: 'Mode') -> None:
    _mode_signal.send(mode)
