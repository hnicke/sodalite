import logging
import time
from pathlib import Path
from threading import Lock, Thread
from typing import Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from sodalite.core.entry import Entry
from sodalite.util import pubsub

_logger = logging.getLogger(__name__)


class DeduplicatedReload:
    _last_reload: float = 0

    def __init__(self, deduplication_interval_millis: int):
        self._needs_reload = False
        self.poller = Thread(target=self._reload_thread, args=(deduplication_interval_millis,), daemon=True)
        self.poller.start()

    def _reload_thread(self, poll_millis: int) -> None:
        while True:
            time.sleep(poll_millis / 1000)
            if self._needs_reload:
                pubsub.filesystem_send()
                self._needs_reload = False

    def reload(self) -> None:
        self._needs_reload = True


class PathHandler(FileSystemEventHandler):  # type: ignore

    def __init__(self, deduplication_interval_millis: int):
        self.reloader = DeduplicatedReload(deduplication_interval_millis)

    def on_modified(self, event: FileSystemEvent) -> None:
        self.reloader.reload()


class EntryWatcher:

    def __init__(self, deduplication_interval_millis: int = 100) -> None:
        self._observer = Observer()
        self._observer.start()

        self._observed_path: Optional[Path] = None
        self._handler = PathHandler(deduplication_interval_millis)

        self._update_lock = Lock()
        pubsub.entry_connect(self.on_navigated)

    def on_navigated(self, entry: Entry) -> None:
        with self._update_lock:
            if self._observed_path == str(entry.path):
                return
            self._observer.unschedule_all()
            self._observed_path = None
            path = entry.path
            if not path.is_dir():
                # version 0.9.0 of watchdog crashes when trying to observe a file
                path = path.parent
            if path.exists():
                self._observer.schedule(self._handler, str(path), recursive=False)
                self._observed_path = path
