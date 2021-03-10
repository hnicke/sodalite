import time
from pathlib import Path
from threading import Thread
from unittest.mock import Mock

from sodalite.core.entrywatcher import DeduplicatedReload, EntryWatcher


def test_deduplicated_reload() -> None:
    navigator = Mock()
    reloader = DeduplicatedReload(navigator, deduplication_interval_millis=100)

    # fire multiple reloads in parallel
    threads = [Thread(target=lambda: reloader.reload()) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    time.sleep(reloader.deduplication_interval_millis / 1000)

    # should only reload the navigator once
    navigator.reload_current_entry.assert_called_once()


def test_file_created(tmp_path: Path) -> None:
    watcher = EntryWatcher(deduplication_interval_millis=10)
    navigator = Mock()
    navigator.current_entry.path = tmp_path
    watcher.on_update(navigator)
    (tmp_path / 'test.txt').write_text('test')
    time.sleep(watcher.deduplication_interval_millis / 1000 * 2)
    navigator.reload_current_entry.assert_called_once()
