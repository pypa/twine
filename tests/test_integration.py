import sys

import colorama
import pretend
import pytest
import requests

from twine import __main__ as dunder_main
from twine import cli


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


twine_sampleproject_token = (
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
        twine_sampleproject_token,
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
        "HTTPError from https://test.pypi.org/legacy/: 403 Client Error\n"
        "Invalid or non-existent authentication information. "
        "See https://test.pypi.org/help/#invalid-auth for details"
    )

    assert dunder_main.main() == colorama.Fore.RED + message + colorama.Style.RESET_ALL


def test_pypi_error_fallback(sampleproject_dist, monkeypatch):
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

    monkeypatch.setattr(cli, "dispatch", pretend.raiser(requests.HTTPError("403")))

    message = "HTTPError: 403"
    assert dunder_main.main() == colorama.Fore.RED + message + colorama.Style.RESET_ALL


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
