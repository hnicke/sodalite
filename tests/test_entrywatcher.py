import time
from pathlib import Path
from threading import Thread
from unittest.mock import Mock

from sodalite.core.entry import Entry
from sodalite.core.entrywatcher import DeduplicatedReload, EntryWatcher
from sodalite.util import topic


def test_deduplicated_reload(callback: Mock) -> None:
    topic.filesystem.connect(callback)

    reloader = DeduplicatedReload(100)

    # fire multiple reloads in parallel
    threads = [Thread(target=lambda: reloader.reload()) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    time.sleep(reloader.deduplication_interval_millis / 1000)

    callback.assert_called_once()


def test_file_created(tmp_path: Path) -> None:
    callback = Mock(spec=lambda: None)
    topic.filesystem.connect(callback)

    watcher = EntryWatcher(10)
    watcher.on_navigated(Entry(tmp_path))
    (tmp_path / 'test.txt').write_text('test')
    time.sleep(watcher.deduplication_interval_millis / 1000 * 2)

    callback.assert_called_once()
