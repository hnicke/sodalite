import logging

from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class DirHandler(FileSystemEventHandler):

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator

    def on_created(self, event):
        logger.debug('Event (entry created): {}'.format(event.src_path))
        self.navigator.reload_current_entry()

    def on_modified(self, event):
        logger.debug('Event (entry modifiedl): {}'.format(event.src_path))
        self.navigator.reload_current_entry()

    def on_deleted(self, event):
        logger.debug('Event (entry deleted): {}'.format(event.src_path))
        self.navigator.reload_current_entry()


class FileHandler(PatternMatchingEventHandler):

    def __init__(self, navigator: 'Navigator', path: str):
        self.navigator = navigator
        super().__init__(patterns=[path], case_sensitive=True)

    def on_deleted(self, event):
        logger.debug('Event (file deleted): {}'.format(event.src_path))
        self.navigator.visit_parent()

    def on_modified(self, event):
        logger.debug('Event (file modified): {}'.format(event.src_path))
        self.navigator.reload_current_entry()


class EntryWatcher:

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator
        self.observer = Observer()
        self.observer.start()

        self.entry = None
        self.watch = None

    def on_update(self):
        if self.watch and self.entry == self.navigator.current_entry:
            return
        if self.watch:
            self.unregister(self.watch)
        self.watch = None
        self.entry = self.navigator.current_entry
        self.watch = self.register()

    def unregister(self, watch):
        if self.watch:
            self.observer.unschedule(watch)

    def register(self):
        entry = self.navigator.current_entry
        if entry.is_dir():
            path = entry.path
            handler = DirHandler(self.navigator)
            logger.debug('Watching {} for changes'.format(entry.path))
        else:
            path = entry.dir
            handler = FileHandler(self.navigator, entry.path)
        watch = self.observer.schedule(handler, path, recursive=False)
        return watch
