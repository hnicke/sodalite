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

    def __init__(self, navigator: 'Navigator', deduplication_interval_millis: int):
        self.deduplication_interval_millis = deduplication_interval_millis
        self.navigator = navigator

    def reload(self) -> None:
        current_time = time.time()
        if self._lock.locked():
            return
        with self._lock:
            if self._last_reload + self.deduplication_interval_millis / 1000 < current_time:
                time.sleep(self.deduplication_interval_millis / 1000)
                self._last_reload = time.time()
                self.navigator.reload_current_entry()


class PathHandler(FileSystemEventHandler):

    def __init__(self, navigator: 'Navigator', deduplication_interval_millis: int):
        self.reloader = DeduplicatedReload(navigator, deduplication_interval_millis)

    def on_any_event(self, event: FileSystemEvent) -> None:
        _logger.debug(f"Event ({event.event_type}): {event.src_path}")
        self.reloader.reload()


class EntryWatcher:

    def __init__(self, deduplication_interval_millis: int = 100) -> None:
        self.deduplication_interval_millis = deduplication_interval_millis
        self._observer = Observer()
        self._observer.start()

        self._watch: Optional[ObservedWatch] = None
        self._update_lock = Lock()

    def on_update(self, navigator: 'Navigator') -> None:
        with self._update_lock:
            path = navigator.current_entry.path
            if self._watch:
                if self._watch.path == str(path):
                    return
                self._observer.unschedule(self._watch)
                self._watch = None
            handler = PathHandler(navigator, deduplication_interval_millis=self.deduplication_interval_millis)
            self._watch = self._observer.schedule(handler, path, recursive=False)
