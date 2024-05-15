# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path

import pretend
import pytest
import requests

from twine import exceptions
from twine import utils

from . import helpers


def test_get_config(write_config_file):
    config_file = write_config_file(
        """
        [distutils]
        index-servers = pypi

        [pypi]
        username = testuser
        password = testpassword
        """
    )

    assert utils.get_config(config_file) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": "testuser",
            "password": "testpassword",
        },
    }


def test_get_config_no_distutils(write_config_file):
    """Upload by default to PyPI if an index server is not set in .pypirc."""
    config_file = write_config_file(
        """
        [pypi]
        username = testuser
        password = testpassword
        """
    )

    assert utils.get_config(config_file) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": "testuser",
            "password": "testpassword",
        },
        "testpypi": {
            "repository": utils.TEST_REPOSITORY,
            "username": None,
            "password": None,
        },
    }


def test_get_config_no_section(write_config_file):
    config_file = write_config_file(
        """
        [distutils]
        index-servers = pypi foo

        [pypi]
        username = testuser
        password = testpassword
        """
    )

    assert utils.get_config(config_file) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": "testuser",
            "password": "testpassword",
        },
    }


def test_get_config_override_pypi_url(write_config_file):
    config_file = write_config_file(
        """
        [pypi]
        repository = http://pypiproxy
        """
    )

    assert utils.get_config(config_file)["pypi"]["repository"] == "http://pypiproxy"


def test_get_config_missing(config_file):
    assert utils.get_config(config_file) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": None,
            "password": None,
        },
        "testpypi": {
            "repository": utils.TEST_REPOSITORY,
            "username": None,
            "password": None,
        },
    }


def test_empty_userpass(write_config_file):
    """Suppress prompts if empty username and password are provided in .pypirc."""
    config_file = write_config_file(
        """
        [pypi]
        username=
        password=
        """
    )

    config = utils.get_config(config_file)
    pypi = config["pypi"]

    assert pypi["username"] == pypi["password"] == ""


def test_get_repository_config_missing(config_file):
    repository_url = "https://notexisting.python.org/pypi"
    exp = {
        "repository": repository_url,
        "username": None,
        "password": None,
    }
    assert utils.get_repository_from_config(config_file, "foo", repository_url) == exp
    assert utils.get_repository_from_config(config_file, "pypi", repository_url) == exp

    exp = {
        "repository": utils.DEFAULT_REPOSITORY,
        "username": None,
        "password": None,
    }
    assert utils.get_repository_from_config(config_file, "pypi") == exp


def test_get_repository_config_url_with_auth(config_file):
    repository_url = "https://user:pass@notexisting.python.org/pypi"
    exp = {
        "repository": "https://notexisting.python.org/pypi",
        "username": "user",
        "password": "pass",
    }
    assert utils.get_repository_from_config(config_file, "foo", repository_url) == exp
    assert utils.get_repository_from_config(config_file, "pypi", repository_url) == exp


@pytest.mark.parametrize(
    "input_url, expected_url",
    [
        ("https://upload.pypi.org/legacy/", "https://upload.pypi.org/legacy/"),
        (
            "https://user:pass@upload.pypi.org/legacy/",
            "https://********@upload.pypi.org/legacy/",
        ),
    ],
)
def test_sanitize_url(input_url: str, expected_url: str) -> None:
    assert utils.sanitize_url(input_url) == expected_url


@pytest.mark.parametrize(
    "repo_url, message",
    [
        (
            "ftp://test.pypi.org",
            r"scheme was required to be one of \['http', 'https'\]",
        ),
        ("https:/", "host was required but missing."),
        ("//test.pypi.org", "scheme was required but missing."),
        ("foo.bar", "host, scheme were required but missing."),
    ],
)
def test_get_repository_config_with_invalid_url(config_file, repo_url, message):
    """Raise an exception for a URL with an invalid/missing scheme and/or host."""
    with pytest.raises(
        exceptions.UnreachableRepositoryURLDetected,
        match=message,
    ):
        utils.get_repository_from_config(config_file, "pypi", repo_url)


def test_get_repository_config_missing_repository(write_config_file):
    """Raise an exception when a custom repository isn't defined in .pypirc."""
    config_file = write_config_file("")
    with pytest.raises(
        exceptions.InvalidConfiguration,
        match="Missing 'missing-repository'",
    ):
        utils.get_repository_from_config(config_file, "missing-repository")


@pytest.mark.parametrize("repository", ["pypi", "missing-repository"])
def test_get_repository_config_missing_file(repository):
    """Raise an exception when a custom config file doesn't exist."""
    with pytest.raises(
        exceptions.InvalidConfiguration,
        match=r"No such file.*missing-file",
    ):
        utils.get_repository_from_config("missing-file", repository)


def test_get_config_deprecated_pypirc():
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    deprecated_pypirc_path = os.path.join(tests_dir, "fixtures", "deprecated-pypirc")

    assert utils.get_config(deprecated_pypirc_path) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": "testusername",
            "password": "testpassword",
        },
        "testpypi": {
            "repository": utils.TEST_REPOSITORY,
            "username": "testusername",
            "password": "testpassword",
        },
    }


@pytest.mark.parametrize(
    ("cli_value", "config", "key", "strategy", "expected"),
    (
        ("cli", {}, "key", lambda: "fallback", "cli"),
        (None, {"key": "value"}, "key", lambda: "fallback", "value"),
        (None, {}, "key", lambda: "fallback", "fallback"),
    ),
)
def test_get_userpass_value(cli_value, config, key, strategy, expected):
    ret = utils.get_userpass_value(cli_value, config, key, strategy)
    assert ret == expected


@pytest.mark.parametrize(
    ("env_name", "default", "environ", "expected"),
    [
        ("MY_PASSWORD", None, {}, None),
        ("MY_PASSWORD", None, {"MY_PASSWORD": "foo"}, "foo"),
        ("URL", "https://example.org", {}, "https://example.org"),
        ("URL", "https://example.org", {"URL": "https://pypi.org"}, "https://pypi.org"),
    ],
)
def test_default_to_environment_action(env_name, default, environ, expected):
    option_strings = ("-x", "--example")
    dest = "example"
    with helpers.set_env(**environ):
        action = utils.EnvironmentDefault(
            env=env_name,
            default=default,
            option_strings=option_strings,
            dest=dest,
        )
    assert action.env == env_name
    assert action.default == expected


@pytest.mark.parametrize(
    "repo_url", ["https://pypi.python.org", "https://testpypi.python.org"]
)
def test_check_status_code_for_deprecated_pypi_url(repo_url):
    response = pretend.stub(status_code=410, url=repo_url)

    # value of Verbose doesn't matter for this check
    with pytest.raises(exceptions.UploadToDeprecatedPyPIDetected):
        utils.check_status_code(response, False)


@pytest.mark.parametrize(
    "repo_url",
    ["https://pypi.python.org", "https://testpypi.python.org"],
)
@pytest.mark.parametrize(
    "verbose",
    [True, False],
)
def test_check_status_code_for_missing_status_code(
    caplog, repo_url, verbose, make_settings, config_file
):
    """Print HTTP errors based on verbosity level."""
    response = pretend.stub(
        status_code=403,
        url=repo_url,
        raise_for_status=pretend.raiser(requests.HTTPError),
        text="Forbidden",
    )

    make_settings(verbose=verbose)

    with pytest.raises(requests.HTTPError):
        utils.check_status_code(response, verbose)

        message = (
            "Error during upload. Retry with the --verbose option for more details."
        )
        assert caplog.messages.count(message) == 0 if verbose else 1


@pytest.mark.parametrize(
    ("size_in_bytes, formatted_size"),
    [(3704, "3.6 KB"), (1153433, "1.1 MB"), (21412841, "20.4 MB")],
)
def test_get_file_size(size_in_bytes, formatted_size, monkeypatch):
    """Get the size of file as a string with units."""
    monkeypatch.setattr(os.path, "getsize", lambda _: size_in_bytes)

    file_size = utils.get_file_size(size_in_bytes)

    assert file_size == formatted_size
