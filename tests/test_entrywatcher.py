from threading import Thread
from unittest.mock import Mock

from sodalite.core.entrywatcher import DeduplicatedReload


def test_deduplicated_reload():
    navigator = Mock()
    reloader = DeduplicatedReload(navigator)

    # fire multiple reloads in parallel
    threads = [Thread(target=lambda: reloader.reload()) for _ in range(20)]
    [x.start() for x in threads]
    [x.join() for x in threads]

    # should only reload the navigator once
    navigator.reload_current_entry.assert_called_once()
