import contextlib
import datetime
import functools
import getpass
import pathlib
import secrets
import subprocess
import sys
import textwrap

import jaraco.envs
import munch
import portend
import pytest
import requests

from twine import settings


@pytest.fixture()
def pypirc(tmpdir):
    return tmpdir / ".pypirc"


@pytest.fixture()
def make_settings(pypirc):
    """Return a factory function for settings.Settings with defaults."""
    default_pypirc = """
        [pypi]
        username:foo
        password:bar
    """

    def _settings(pypirc_text=default_pypirc, **settings_kwargs):
        pypirc.write(textwrap.dedent(pypirc_text))

        settings_kwargs.setdefault("sign_with", None)
        settings_kwargs.setdefault("config_file", str(pypirc))

        return settings.Settings(**settings_kwargs)

    return _settings


class DevPiEnv(jaraco.envs.ToxEnv):
    """Run devpi using tox:testenv:devpi."""

    name = "devpi"
    username = "foober"

    def create(self, root, password):
        super().create()
        self.base = root
        self.password = password
        self.port = portend.find_available_local_port()
        cmd = [
            self.exe("devpi-init"),
            "--serverdir",
            str(root),
            "--root-passwd",
            password,
        ]
        subprocess.run(cmd, check=True)

    @property
    def url(self):
        return f"http://localhost:{self.port}/"

    @property
    def repo(self):
        return f"{self.url}/{self.username}/dev/"

    def ready(self):
        with contextlib.suppress(Exception):
            return requests.get(self.url)

    def init(self):
        run = functools.partial(subprocess.run, check=True)
        client_dir = self.base / "client"
        devpi_client = [
            self.exe("devpi"),
            "--clientdir",
            str(client_dir),
        ]
        run(devpi_client + ["use", self.url + "root/pypi/"])
        run(
            devpi_client
            + ["user", "--create", self.username, f"password={self.password}"]
        )
        run(devpi_client + ["login", self.username, "--password", self.password])
        run(devpi_client + ["index", "-c", "dev"])


@pytest.fixture(scope="session")
def devpi_server(request, watcher_getter, tmp_path_factory):
    env = DevPiEnv()
    password = secrets.token_urlsafe()
    root = tmp_path_factory.mktemp("devpi")
    env.create(root, password)
    proc = watcher_getter(
        name=str(env.exe("devpi-server")),
        arguments=["--port", str(env.port), "--serverdir", str(root)],
        checker=env.ready,
        # Needed for the correct execution order of finalizers
        request=request,
    )
    env.init()
    username = env.username
    url = env.repo
    return munch.Munch.fromDict(locals())


dist_names = [
    "twine-1.5.0.tar.gz",
    "twine-1.5.0-py2.py3-none-any.whl",
    "twine-1.6.5.tar.gz",
    "twine-1.6.5-py2.py3-none-any.whl",
]


@pytest.fixture(params=dist_names)
def uploadable_dist(request):
    return pathlib.Path(__file__).parent / "fixtures" / request.param


@pytest.fixture
def entered_password(monkeypatch):
    monkeypatch.setattr(getpass, "getpass", lambda prompt: "entered pw")


@pytest.fixture(scope="session")
def sampleproject_dist(tmp_path_factory):
    checkout = tmp_path_factory.mktemp("sampleproject", numbered=False)
    subprocess.run(
        ["git", "clone", "https://github.com/pypa/sampleproject", str(checkout)]
    )
    with (checkout / "setup.py").open("r+") as setup:
        orig = setup.read()
        sub = orig.replace("name='sampleproject'", "name='twine-sampleproject'")
        assert orig != sub
        setup.seek(0)
        setup.write(sub)
    tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    subprocess.run(
        [sys.executable, "setup.py", "egg_info", "--tag-build", f"post{tag}", "sdist"],
        cwd=str(checkout),
    )
    (dist,) = checkout.joinpath("dist").glob("*")
    return dist


class PypiserverEnv(jaraco.envs.ToxEnv):
    """Run pypiserver using tox:testenv:pypiserver."""

    name = "pypiserver"

    @property
    @functools.lru_cache()
    def port(self):
        return portend.find_available_local_port()

    @property
    def url(self):
        return f"http://localhost:{self.port}/"

    def ready(self):
        with contextlib.suppress(Exception):
            return requests.get(self.url)


@pytest.fixture(scope="session")
def pypiserver_instance(request, watcher_getter, tmp_path_factory):
    env = PypiserverEnv()
    env.create()
    proc = watcher_getter(
        name=str(env.exe("pypi-server")),
        arguments=[
            "--port",
            str(env.port),
            # allow anonymous uploads
            "-P",
            ".",
            "-a",
            ".",
            tmp_path_factory.mktemp("packages"),
        ],
        checker=env.ready,
        # Needed for the correct execution order of finalizers
        request=request,
    )
    url = env.url
    return munch.Munch.fromDict(locals())
