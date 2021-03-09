from pathlib import Path
from threading import Thread
from unittest.mock import Mock

from sodalite.core.entrywatcher import DeduplicatedReload, EntryWatcher


def test_deduplicated_reload() -> None:
    navigator = Mock()
    reloader = DeduplicatedReload(navigator)

    # fire multiple reloads in parallel
    threads = [Thread(target=lambda: reloader.reload()) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # should only reload the navigator once
    navigator.reload_current_entry.assert_called_once()


def test_entry_watcher(tmp_path: Path) -> None:
    watcher = EntryWatcher()
    navigator = Mock()
    # watcher.on_update(navigator)
