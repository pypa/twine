import contextlib
import datetime
import functools
import pathlib
import re
import secrets
import subprocess
import sys

import colorama
import jaraco.envs
import munch
import portend
import pytest
import requests

from twine import __main__ as dunder_main
from twine import cli

pytestmark = [pytest.mark.enable_socket, pytest.mark.flaky(reruns=3, reruns_delay=1)]


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


def test_pypi_error(sampleproject_dist, monkeypatch):
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
        re.escape(colorama.Fore.RED)
        + r"HTTPError: 403 Forbidden from https://test\.pypi\.org/legacy/\n"
        + r".+?authentication"
    )

    result = dunder_main.main()

    assert re.match(message, result)


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


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="pytest-services watcher_getter fixture does not support Windows",
)
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


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="pytest-services watcher_getter fixture does not support Windows",
)
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
