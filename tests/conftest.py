import textwrap

import pytest

from twine import settings


@pytest.fixture()
def pypirc(tmpdir):
    return tmpdir / ".pypirc"


@pytest.fixture()
def make_settings(pypirc):
    """Returns a factory function for settings.Settings with defaults."""

    default_pypirc = """
        [pypi]
        username:foo
        password:bar
    """

    def _settings(pypirc_text=default_pypirc, **settings_kwargs):
        pypirc.write(textwrap.dedent(pypirc_text))

        settings_kwargs.setdefault('sign_with', None)
        settings_kwargs.setdefault('config_file', str(pypirc))

        return settings.Settings(**settings_kwargs)

    return _settings
