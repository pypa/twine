import contextlib
import textwrap

import pytest
import portend
import requests
import jaraco.envs

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


class DevPiEnv(jaraco.envs.ToxEnv):
    """
    Run devpi using tox:testenv:devpi.
    """
    name = 'devpi'

    def create(self):
        super().create()
        self.port = portend.find_available_local_port()

    def ready(self):
        url = 'http://localhost:{port}'.format(port=self.port)
        with contextlib.suppress(Exception):
            return requests.get(url)


@pytest.fixture(scope='session')
def devpi_server(request, watcher_getter):
    env = DevPiEnv()
    env.create()
    proc = watcher_getter(
        name=str(env.exe('devpi-server')),
        arguments=['--port', str(env.port)],
        checker=env.ready,
        # Needed for the correct execution order of finalizers
        request=request,
    )
    return locals()
