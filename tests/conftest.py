from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture

from sodalite.core import config


@fixture(autouse=True)
def config_env_variable(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(config.ENV_CONFIG_FILE, 'docs/sodalite.conf')
