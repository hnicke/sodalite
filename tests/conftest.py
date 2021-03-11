from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture

from sodalite.core import config


@fixture(autouse=True)
def config_env_variable(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(config.ENV_CONFIG_FILE, 'docs/sodalite.conf')


@fixture
def callback() -> Mock:
    return Mock(spec=lambda: None)
