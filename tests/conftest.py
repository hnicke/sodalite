from pathlib import Path
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture

from sodalite.util import env


@fixture(autouse=True)
def config_env_variable(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(env.ENV_CONFIG_FILE, str(Path('../../docs/sodalite.conf').absolute()))


@fixture
def callback() -> Mock:
    return Mock(spec=lambda: None)
