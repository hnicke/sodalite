from typing import Set, Dict, Callable


class Observer:
    def on_update(self):
        pass


class Observable:
    def __init__(self):
        self._observers: Dict[str, Set[Callable]] = {}

    def register(self, callback: Callable, topic=None, immediate_update=True):
        if topic not in self._observers:
            self._observers[topic] = set()
        self._observers[topic].add(callback)
        if immediate_update:
            callback(self)

    def unregister(self, callback: Callable, topic=None):
        if topic in self._observers:
            self._observers[topic].remove(callback)

    def notify_all(self, topic=None):
        if topic in self._observers:
            for callback in self._observers[topic]:
                callback(self)
