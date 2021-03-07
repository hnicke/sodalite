from pathlib import Path

from pytest import fixture

from sodalite.core import History


def test_save_and_load(history: History, history_file: Path):
    history.save(file=history_file)
    loaded_history = History.load(file=history_file)
    assert history == loaded_history


def test_cwd(history: History, entry_1):
    assert history.cwd() == entry_1


def test_visit(history):
    new_entry = Path('/dir/two')
    history.visit(new_entry)
    assert history.cwd() == new_entry


def test_visit_parent(history: History):
    parent = Path('/parent')
    child = parent / 'child'
    history.visit(child)
    history.visit_parent()
    assert history.cwd() == parent


def test_backward(history: History):
    before = history.cwd()
    times = 3
    for i in range(times):
        history.visit(Path(str(i)))
    for _ in range(times):
        history.backward()
    after = history.cwd()
    assert before == after


def test_forward(history: History):
    times = 10
    for i in range(times):
        history.visit(Path(str(i)))
    for _ in range(times):
        history.backward()
    for _ in range(times):
        history.forward()
    assert history.cwd() == Path(str(times - 1))


def test_visit_discard_future(history: History):
    times = 10
    for i in range(times):
        history.visit(Path(str(i)))
    for i in range(5):
        history.backward()
    # this should truncate the 'future' history
    history.visit(Path('truncate-entry'))
    entry = history.cwd()
    history.forward()
    forward_entry = history.cwd()
    # there should be no history
    assert entry == forward_entry


def test_visit_same(history: History, entry_1: Path):
    new_entry = Path('/dir/two')
    history.visit(new_entry)
    history.visit(new_entry)
    history.backward()
    assert history.cwd() == entry_1


@fixture
def history_file(tmp_path: Path) -> Path:
    return tmp_path / 'history.json'


@fixture
def entry_1() -> Path:
    return Path('/dir/one')


@fixture
def history(entry_1: Path) -> History:
    return History([entry_1])
