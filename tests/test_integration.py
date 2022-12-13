import contextlib
import datetime
import functools
import pathlib
import platform
import re
import secrets
import subprocess
import sys
import venv
from types import SimpleNamespace

# TODO: Drop jaraco.envs and munch, and update tox.ini
import jaraco.envs
import munch
import portend
import pytest
import requests

from twine import __main__ as dunder_main
from twine import cli

pytestmark = [pytest.mark.enable_socket]


@pytest.fixture(scope="session")
def sampleproject_dist(tmp_path_factory: pytest.TempPathFactory):
    checkout = tmp_path_factory.mktemp("sampleproject", numbered=False)
    tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    subprocess.run(
        ["git", "clone", "https://github.com/pypa/sampleproject", str(checkout)],
        check=True,
    )

    pyproject = checkout / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text()
        .replace(
            'name = "sampleproject"',
            'name = "twine-sampleproject"',
        )
        .replace(
            'version = "3.0.0"',
            f'version = "3.0.0post{tag}"',
        )
    )

    subprocess.run(
        [sys.executable, "-m", "build", "--sdist"],
        check=True,
        cwd=str(checkout),
    )

    [dist, *_] = (checkout / "dist").glob("*")
    assert dist.name == f"twine-sampleproject-3.0.0.post{tag}.tar.gz"

    return dist


sampleproject_token = (
    "pypi-AgENdGVzdC5weXBpLm9yZwIkNDgzYTFhMjEtMzEwYi00NT"
    "kzLTkwMzYtYzc1Zjg4NmFiMjllAAJEeyJwZXJtaXNzaW9ucyI6IH"
    "sicHJvamVjdHMiOiBbInR3aW5lLXNhbXBsZXByb2plY3QiXX0sIC"
    "J2ZXJzaW9uIjogMX0AAAYg2kBZ1tN8lj8dlmL3ScoVvr_pvQE0t"
    "6PKqigoYJKvw3M"
)


def test_pypi_upload(sampleproject_dist):
    command = [
        "upload",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "--username",
        "__token__",
        "--password",
        sampleproject_token,
        str(sampleproject_dist),
    ]
    cli.dispatch(command)


def test_pypi_error(sampleproject_dist, monkeypatch, capsys):
    command = [
        "twine",
        "upload",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "--username",
        "foo",
        "--password",
        "bar",
        str(sampleproject_dist),
    ]
    monkeypatch.setattr(sys, "argv", command)

    message = (
        r"HTTPError: 403 Forbidden from https://test\.pypi\.org/legacy/"
        + r".+authentication information"
    )

    error = dunder_main.main()
    assert error

    captured = capsys.readouterr()

    assert re.search(message, captured.out, re.DOTALL)


@pytest.fixture(
    params=[
        "twine-1.5.0.tar.gz",
        "twine-1.5.0-py2.py3-none-any.whl",
        "twine-1.6.5.tar.gz",
        "twine-1.6.5-py2.py3-none-any.whl",
    ]
)
def uploadable_dist(request):
    return pathlib.Path(__file__).parent / "fixtures" / request.param


skip_setup_error = pytest.mark.skip(
    reason="Failing; https://github.com/pypa/twine/issues/684#issuecomment-1347247791"
)

xfail_win32 = pytest.mark.xfail(
    sys.platform == "win32",
    reason="pytest-services watcher_getter fixture does not support Windows",
)


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


@skip_setup_error
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


@skip_setup_error
@xfail_win32
def test_devpi_upload(devpi_server, uploadable_dist):
    command = [
        "upload",
        "--repository-url",
        devpi_server.url,
        "--username",
        devpi_server.username,
        "--password",
        devpi_server.password,
        str(uploadable_dist),
    ]
    cli.dispatch(command)


@pytest.fixture(scope="session")
def pypiserver_instance(request, watcher_getter, tmp_path_factory):
    env_dir = tmp_path_factory.mktemp("venv")
    bin_dir = env_dir / ("Scripts" if platform.system() == "Windows" else "bin")

    venv.create(env_dir, symlinks=True, with_pip=True, upgrade_deps=True)
    subprocess.run(
        [bin_dir / "python", "-m", "pip", "install", "pypiserver"], check=True
    )

    port = portend.find_available_local_port()
    url = f"http://localhost:{port}/"

    def ready():
        with contextlib.suppress(Exception):
            return requests.get(url)

    watcher_getter(
        name=str(bin_dir / "pypi-server"),
        arguments=[
            "--port",
            str(port),
            # allow anonymous uploads
            "-P",
            ".",
            "-a",
            ".",
            tmp_path_factory.mktemp("packages"),
        ],
        checker=ready,
        # Needed for the correct execution order of finalizers
        request=request,
    )

    return SimpleNamespace(url=url)


@xfail_win32
def test_pypiserver_upload(pypiserver_instance, uploadable_dist):
    command = [
        "upload",
        "--repository-url",
        pypiserver_instance.url,
        "--username",
        "any",
        "--password",
        "any",
        str(uploadable_dist),
    ]
    cli.dispatch(command)
