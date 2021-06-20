import getpass
import textwrap

import pytest

from twine import settings


@pytest.fixture()
def config_file(tmpdir):
    return tmpdir / ".pypirc"


@pytest.fixture
def write_config_file(config_file):
    def _write(config):
        config_file.write(textwrap.dedent(config))
        return config_file

    return _write


@pytest.fixture()
def make_settings(write_config_file):
    """Return a factory function for settings.Settings with defaults."""
    default_config = """
        [pypi]
        username:foo
        password:bar
    """

    def _settings(config=default_config, **settings_kwargs):
        config_file = write_config_file(config)

        settings_kwargs.setdefault("sign_with", None)
        settings_kwargs.setdefault("config_file", config_file)

        return settings.Settings(**settings_kwargs)

    return _settings


@pytest.fixture
def entered_password(monkeypatch):
    monkeypatch.setattr(getpass, "getpass", lambda prompt: "entered pw")
