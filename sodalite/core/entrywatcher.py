import logging
import time
from pathlib import Path
from threading import Lock

from typing import TYPE_CHECKING, Optional
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler, DirModifiedEvent, DirDeletedEvent, \
    DirCreatedEvent, FileDeletedEvent, FileModifiedEvent
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from sodalite.core.entry import Entry

if TYPE_CHECKING:
    from sodalite.core.navigate import Navigator

_logger = logging.getLogger(__name__)


class DeduplicatedReload:
    _lock = Lock()
    _last_reload: float = 0
    _deduplication_interval_seconds = 0.1

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator

    def reload(self) -> None:
        current_time = time.time()
        if self._lock.locked():
            return
        with self._lock:
            if self._last_reload + self._deduplication_interval_seconds < current_time:
                time.sleep(self._deduplication_interval_seconds)
                self._last_reload = time.time()
                self.navigator.reload_current_entry()


class DirHandler(FileSystemEventHandler):

    def __init__(self, navigator: 'Navigator'):
        self.reloader = DeduplicatedReload(navigator)

    def on_created(self, event: DirCreatedEvent) -> None:
        _logger.debug('Event (dir created): {}'.format(event.src_path))
        self.reloader.reload()

    def on_modified(self, event: DirModifiedEvent) -> None:
        _logger.debug('Event (dir modified): {}'.format(event.src_path))
        self.reloader.reload()

    def on_deleted(self, event: DirDeletedEvent) -> None:
        _logger.debug('Event (dir deleted): {}'.format(event.src_path))
        self.reloader.reload()


class FileHandler(PatternMatchingEventHandler):

    def __init__(self, navigator: 'Navigator', path: Path):
        self.reloader = DeduplicatedReload(navigator)
        super(FileHandler, self).__init__(patterns=[str(path)], case_sensitive=True)

    def on_deleted(self, event: FileDeletedEvent) -> None:
        _logger.debug(f"Event (file deleted): {event.src_path}")
        self.reloader.reload()

    def on_modified(self, event: FileModifiedEvent) -> None:
        _logger.debug(f"Event (file modified): {event.src_path}")
        self.reloader.reload()


class EntryWatcher:

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator
        self.observer = Observer()
        self.observer.start()

        self.entry: Optional[Entry] = None
        self.watch: Optional[ObservedWatch] = None

    def on_update(self, _: 'Navigator') -> None:
        if self.watch and self.entry == self.navigator.current_entry:
            return
        if self.watch:
            self.unregister(self.watch)
        self.entry = self.navigator.current_entry
        self.watch = self.register()

    def unregister(self, watch: ObservedWatch) -> None:
        if self.watch:
            self.observer.unschedule(watch)
            self.watch = None

    def register(self) -> ObservedWatch:
        entry = self.navigator.current_entry
        if entry.is_dir():
            handler = DirHandler(self.navigator)
            _logger.debug(f"Watching {entry.path} for changes")
        else:
            handler = FileHandler(self.navigator, entry.path)
        watch = self.observer.schedule(handler, entry.path, recursive=False)
        return watch
