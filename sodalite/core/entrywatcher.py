import logging

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class Handler(FileSystemEventHandler):

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator

    def on_created(self, event):
        logger.info('Event (entry created): {}'.format(event.src_path))
        self.navigator.reload_current_entry()

    def on_deleted(self, event):
        logger.info('Event (entry deleted): {}'.format(event.src_path))
        self.navigator.reload_current_entry()


class EntryWatcher:

    def __init__(self, navigator: 'Navigator'):
        self.navigator = navigator
        self.observer = Observer()
        self.observer.start()

        self.watching = None

    def on_update(self):
        if self.watching and self.watching[2] == self.navigator.current_entry:
            return
        if self.watching:
            self.unregister(*self.watching)
        self.watching = None
        self.watching = self.register()

    def unregister(self, handler, watch, entry):
        if self.watching:
            self.observer.remove_handler_for_watch(handler, watch)
            logger.debug('Stop watching {}'.format(entry.path))

    def register(self):
        entry = self.navigator.current_entry
        if entry.is_dir():
            handler = Handler(self.navigator)
            watch = self.observer.schedule(handler, entry.path, recursive=False)
            logger.debug('Watching {} for changes'.format(entry.path))
            return handler, watch, entry
