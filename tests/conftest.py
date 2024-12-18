import getpass
import logging.config
import pathlib
import tempfile
import textwrap

import pytest
import rich

from twine import settings
from twine import utils

from .helpers import build_sdist
from .helpers import build_wheel


@pytest.fixture(autouse=True)
def configure_output():
    """
    Disable colored output and line wrapping before each test.

    Some tests (e.g. test_main.py) will end up calling (and making assertions based on)
    twine.cli.configure_output, which overrides this configuration. This fixture should
    prevent that leaking into subsequent tests.
    """
    rich.reconfigure(
        no_color=True,
        color_system=None,
        emoji=False,
        highlight=False,
        width=500,
    )

    logging.config.dictConfig(
        {
            "version": 1,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                }
            },
            "loggers": {
                "twine": {
                    "handlers": ["console"],
                },
            },
        }
    )


@pytest.fixture()
def config_file(tmpdir, monkeypatch):
    path = tmpdir / ".pypirc"
    # Mimic common case of .pypirc in home directory
    monkeypatch.setattr(utils, "DEFAULT_CONFIG_FILE", path)
    return path


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


@pytest.fixture(scope="session")
def tmp_path_session(tmp_path_factory):
    return pathlib.Path(
        tempfile.mkdtemp(
            prefix="twine-test-",
            dir=tmp_path_factory.mktemp("test"),
        )
    )


@pytest.fixture
def test_wheel(tmp_path_session):
    return build_wheel(tmp_path_session, "test", "1.2.3", {})


@pytest.fixture
def test_wheel_signature(test_wheel):
    signature = test_wheel.with_suffix(".whl.asc")
    signature.write_text("-----BEGIN PGP SIGNATURE-----")
    yield signature
    signature.unlink()


@pytest.fixture
def test_sdist(tmp_path_session):
    return build_sdist(tmp_path_session, "test", "1.2.3", {})
