from enum import Enum
from typing import Callable, Optional, Union


class Observer:
    def on_update(self, observable: 'Observable') -> None:
        pass


Callback = Callable[['Observable'], None]


def _sanitize_topic(topic: Optional[Union[str, Enum]]) -> Optional[str]:
    return topic.value if isinstance(topic, Enum) else topic


class Observable:
    def __init__(self) -> None:
        self._observers: dict[Optional[str], set[Callback]] = {}

    def register(self, callback: Callback, topic: Union[str, Enum] = None, immediate_update: bool = True) -> None:
        self._observers.setdefault(_sanitize_topic(topic), set()).add(callback)
        if immediate_update:
            callback(self)

    def unregister(self, callback: Callback, topic: str = None) -> None:
        if topic in self._observers:
            self._observers[topic].remove(callback)

    def notify_all(self, topic: Optional[Union[str, Enum]] = None) -> None:
        t = _sanitize_topic(topic)
        if t in self._observers:
            for callback in self._observers[t]:
                callback(self)
