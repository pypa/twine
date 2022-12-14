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

import pytest
import requests

from twine import __main__ as dunder_main
from twine import cli

pytestmark = [pytest.mark.enable_socket]

run = functools.partial(subprocess.run, check=True)

xfail_win32 = pytest.mark.xfail(
    sys.platform == "win32",
    reason="pytest-services watcher_getter fixture does not support Windows",
)


@pytest.fixture(scope="session")
def sampleproject_dist(tmp_path_factory: pytest.TempPathFactory):
    checkout = tmp_path_factory.mktemp("sampleproject", numbered=False)
    tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    run(["git", "clone", "https://github.com/pypa/sampleproject", checkout])

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

    run([sys.executable, "-m", "build", "--sdist"], cwd=checkout)

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


@pytest.fixture(scope="session")
def venv_exe_dir(tmp_path_factory):
    env_dir = tmp_path_factory.mktemp("venv")
    venv.create(env_dir, symlinks=True, with_pip=True)
    return env_dir / ("Scripts" if platform.system() == "Windows" else "bin")


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


@pytest.fixture(scope="session")
def devpi_server(request, venv_exe_dir, port_getter, watcher_getter, tmp_path_factory):
    run([venv_exe_dir / "python", "-m", "pip", "install", "devpi-server", "devpi"])

    server_dir = tmp_path_factory.mktemp("devpi")
    username = "foober"
    password = secrets.token_urlsafe()
    port = port_getter()
    url = f"http://localhost:{port}/"
    repo = f"{url}/{username}/dev/"

    run(
        [
            venv_exe_dir / "devpi-init",
            "--serverdir",
            server_dir,
            "--root-passwd",
            password,
        ]
    )

    def ready():
        with contextlib.suppress(Exception):
            return requests.get(url)

    watcher_getter(
        name=venv_exe_dir / "devpi-server",
        arguments=["--port", str(port), "--serverdir", server_dir],
        checker=ready,
        # Needed for the correct execution order of finalizers
        request=request,
    )

    def devpi_run(cmd):
        return run(
            [
                venv_exe_dir / "devpi",
                "--clientdir",
                server_dir / "client",
                *cmd,
            ]
        )

    devpi_run(["use", url + "root/pypi/"])
    devpi_run(["user", "--create", username, f"password={password}"])
    devpi_run(["login", username, "--password", password])
    devpi_run(["index", "-c", "dev"])

    return SimpleNamespace(url=repo, username=username, password=password)


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
def pypiserver_instance(
    request, venv_exe_dir, port_getter, watcher_getter, tmp_path_factory
):
    run([venv_exe_dir / "python", "-m", "pip", "install", "pypiserver"])

    port = port_getter()
    url = f"http://localhost:{port}/"

    def ready():
        with contextlib.suppress(Exception):
            return requests.get(url)

    watcher_getter(
        name=venv_exe_dir / "pypi-server",
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
