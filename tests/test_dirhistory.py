from pathlib import Path

from pytest import fixture

from sodalite.core import DirHistory


def test_save_and_load(history: DirHistory, history_file: Path):
    history.save(file=history_file)
    loaded_history = DirHistory.load(file=history_file)
    assert history == loaded_history


def test_cwd(history: DirHistory, entry_1):
    assert history.cwd() == entry_1


@fixture
def history_file(tmp_path) -> Path:
    return tmp_path / 'history.json'


@fixture
def entry_1() -> str:
    return '/dir/one'


@fixture
def history(entry_1) -> DirHistory:
    return DirHistory([entry_1])
