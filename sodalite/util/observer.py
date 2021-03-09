from typing import Callable, Optional


class Observer:
    def on_update(self) -> None:
        pass


Callback = Callable[['Observable'], None]


class Observable:
    def __init__(self) -> None:
        self._observers: dict[Optional[str], set[Callback]] = {}

    def register(self, callback, topic: str = None, immediate_update=True) -> None:
        if topic not in self._observers:
            self._observers[topic] = set()
        self._observers[topic].add(callback)
        if immediate_update:
            callback(self)

    def unregister(self, callback: Callback, topic=None) -> None:
        if topic in self._observers:
            self._observers[topic].remove(callback)

    def notify_all(self, topic=None) -> None:
        if topic in self._observers:
            for callback in self._observers[topic]:
                callback(self)
