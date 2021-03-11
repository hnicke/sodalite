from sodalite.core import config


def test_config() -> None:
    """Test to parse configuration file"""
    configuration = config.get()
    assert configuration.hooks is not None
    assert configuration.keymap is not None
    assert configuration.preferred_names is not None
