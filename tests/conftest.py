import contextlib
import textwrap
import secrets
import subprocess
import pathlib
import functools
import getpass

import pytest
import portend
import requests
import jaraco.envs
import munch

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
    username = 'foober'

    def create(self, root, password):
        super().create()
        self.base = root
        self.password = password
        self.port = portend.find_available_local_port()
        cmd = [
            self.exe('devpi-init'),
            '--serverdir', str(root),
            '--root-passwd', password,
        ]
        subprocess.run(cmd, check=True)

    @property
    def url(self):
        return f'http://localhost:{self.port}/'

    @property
    def repo(self):
        return f'{self.url}/{self.username}/dev/'

    def ready(self):
        with contextlib.suppress(Exception):
            return requests.get(self.url)

    def init(self):
        run = functools.partial(subprocess.run, check=True)
        client_dir = self.base / 'client'
        devpi_client = [
            self.exe('devpi'),
            '--clientdir', str(client_dir),
        ]
        run(devpi_client + ['use', self.url + 'root/pypi/'])
        run(devpi_client + [
            'user', '--create', self.username, f'password={self.password}'])
        run(devpi_client + [
            'login', self.username, '--password', self.password])
        run(devpi_client + ['index', '-c', 'dev'])


@pytest.fixture(scope='session')
def devpi_server(request, watcher_getter, tmp_path_factory):
    env = DevPiEnv()
    password = secrets.token_urlsafe()
    root = tmp_path_factory.mktemp('devpi')
    env.create(root, password)
    proc = watcher_getter(
        name=str(env.exe('devpi-server')),
        arguments=['--port', str(env.port), '--serverdir', str(root)],
        checker=env.ready,
        # Needed for the correct execution order of finalizers
        request=request,
    )
    env.init()
    username = env.username
    url = env.repo
    return munch.Munch.fromDict(locals())


dist_names = [
    'twine-1.5.0.tar.gz',
    'twine-1.5.0-py2.py3-none-any.whl',
    'twine-1.6.5.tar.gz',
    'twine-1.6.5-py2.py3-none-any.whl',
]


@pytest.fixture(params=dist_names)
def uploadable_dist(request):
    return pathlib.Path(__file__).parent / 'fixtures' / request.param


@pytest.fixture
def entered_password(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: 'entered pw')
