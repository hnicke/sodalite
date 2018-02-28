from typing import Set


class Observer:
    def on_update(self):
        pass


class Observable:
    def __init__(self):
        self._observers: Set[Observer] = set()

    def register(self, observer):
        self._observers.add(observer)
        observer.on_update()

    def unregister(self, observer):
        self._observers.remove(observer)

    def notify_all(self):
        for observer in self._observers:
            observer.on_update()
