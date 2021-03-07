import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler, DirModifiedEvent, DirDeletedEvent, \
    DirCreatedEvent, FileDeletedEvent, FileModifiedEvent
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from sodalite.core.entry import Entry

if TYPE_CHECKING:
    from sodalite.core.navigate import Navigator

logger = logging.getLogger(__name__)


class DirHandler(FileSystemEventHandler):

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator

    # TODO these methods happen to call reload_current_entry() too often if many changes happen
    # this needs some serious debouncing
    def on_created(self, event: DirCreatedEvent):
        logger.debug('Event (entry created): {}'.format(event.src_path))
        self.navigator.reload_current_entry()

    def on_modified(self, event: DirModifiedEvent):
        logger.debug('Event (entry modified): {}'.format(event.src_path))
        self.navigator.reload_current_entry()

    def on_deleted(self, event: DirDeletedEvent):
        logger.debug('Event (entry deleted): {}'.format(event.src_path))
        self.navigator.reload_current_entry()


class FileHandler(PatternMatchingEventHandler):

    def __init__(self, navigator: 'Navigator', path: Path):
        self.navigator = navigator
        super().__init__(patterns=[str(path)], case_sensitive=True)

    def on_deleted(self, event: FileDeletedEvent):
        logger.debug('Event (file deleted): {}'.format(event.src_path))
        self.navigator.visit_parent()

    def on_modified(self, event: FileModifiedEvent):
        logger.debug('Event (file modified): {}'.format(event.src_path))
        self.navigator.reload_current_entry()


class EntryWatcher:

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator
        self.observer = Observer()
        self.observer.start()

        self.entry: Optional[Entry] = None
        self.watch: Optional[ObservedWatch] = None

    def on_update(self, _):
        if self.watch and self.entry == self.navigator.current_entry:
            return
        if self.watch:
            self.unregister(self.watch)
        self.watch = None
        self.entry = self.navigator.current_entry
        self.watch = self.register()

    def unregister(self, watch: ObservedWatch):
        if self.watch:
            self.observer.unschedule(watch)

    def register(self) -> ObservedWatch:
        entry = self.navigator.current_entry
        if entry.is_dir():
            path = entry.path
            handler = DirHandler(self.navigator)
            logger.debug('Watching {} for changes'.format(entry.path))
        else:
            path = entry.dir
            handler = FileHandler(self.navigator, Path(entry.path))
        watch = self.observer.schedule(handler, path, recursive=False)
        return watch
