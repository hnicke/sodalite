from pathlib import Path

from pytest import fixture

from sodalite.core import DirHistory


def test_save_and_load(history: DirHistory, history_file: Path):
    history.save(file=history_file)
    loaded_history = DirHistory.load(file=history_file)
    assert history == loaded_history


@fixture
def history_file(tmp_path) -> Path:
    return tmp_path / 'history.json'


@fixture
def history() -> DirHistory:
    return DirHistory(['/dir/one'])
