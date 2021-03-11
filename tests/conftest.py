from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture


@fixture(autouse=True)
def config(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv('CONFIG_FILE', 'docs/sodalite.conf')
