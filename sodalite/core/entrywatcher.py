import logging
import time
from threading import Lock
from typing import TYPE_CHECKING, Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

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


class PathHandler(FileSystemEventHandler):

    def __init__(self, navigator: 'Navigator'):
        self.reloader = DeduplicatedReload(navigator)

    def on_any_event(self, event: FileSystemEvent) -> None:
        _logger.debug(f"Event ({event.event_type}): {event.src_path}")
        self.reloader.reload()


class EntryWatcher:

    def __init__(self) -> None:
        self.observer = Observer()
        self.observer.start()

        self.watch: Optional[ObservedWatch] = None
        self.update_lock = Lock()

    def on_update(self, navigator: 'Navigator') -> None:
        with self.update_lock:
            path = navigator.current_entry.path
            if self.watch:
                if self.watch.path == str(path):
                    return
                self.observer.unschedule(self.watch)
                self.watch = None
            self.watch = self.observer.schedule(PathHandler(navigator), path, recursive=False)
