# Copyright 2015 Ian Cordasco
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
import logging
from contextlib import contextmanager

import pretend
import pytest
import requests

from twine import repository
from twine import utils


@pytest.fixture()
def default_repo():
    return repository.Repository(
        repository_url=utils.DEFAULT_REPOSITORY,
        username="username",
        password="password",
    )


def test_gpg_signature_structure_is_preserved():
    """Preserve 'gpg_signature' key when converting metadata."""
    data = {
        "gpg_signature": ("filename.asc", "filecontent"),
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [("gpg_signature", ("filename.asc", "filecontent"))]


def test_content_structure_is_preserved():
    """Preserve 'content' key when converting metadata."""
    data = {
        "content": ("filename", "filecontent"),
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [("content", ("filename", "filecontent"))]


def test_iterables_are_flattened():
    """Flatten iterable metadata to list of tuples."""
    data = {
        "platform": ["UNKNOWN"],
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [("platform", "UNKNOWN")]

    data = {
        "platform": ["UNKNOWN", "ANOTHERPLATFORM"],
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [("platform", "UNKNOWN"), ("platform", "ANOTHERPLATFORM")]


def test_set_client_certificate(default_repo):
    """Set client certificate for session."""
    assert default_repo.session.cert is None

    default_repo.set_client_certificate(("/path/to/cert", "/path/to/key"))
    assert default_repo.session.cert == ("/path/to/cert", "/path/to/key")


def test_set_certificate_authority(default_repo):
    """Set certificate authority for session."""
    assert default_repo.session.verify is True

    default_repo.set_certificate_authority("/path/to/cert")
    assert default_repo.session.verify == "/path/to/cert"


def test_make_user_agent_string(default_repo):
    """Add twine and its dependencies to User-Agent session header."""
    assert "User-Agent" in default_repo.session.headers

    user_agent = default_repo.session.headers["User-Agent"]
    packages = (
        "twine/",
        "requests/",
        "requests-toolbelt/",
        "pkginfo/",
        "importlib_metadata/",
        "packaging/",
    )
    assert all(p in user_agent for p in packages)


def response_with(**kwattrs):
    resp = requests.Response()
    for attr, value in kwattrs.items():
        if hasattr(resp, attr):
            setattr(resp, attr, value)

    return resp


def test_package_is_uploaded_404s(default_repo):
    """Return False when the project API response status isn't 200."""
    default_repo.session = pretend.stub(
        get=lambda url, headers: response_with(status_code=404)
    )
    package = pretend.stub(safe_name="fake", metadata=pretend.stub(version="2.12.0"))

    assert default_repo.package_is_uploaded(package) is False


def test_package_is_uploaded_200s_with_no_releases(default_repo):
    """Return False when the list of releases for a project is empty."""
    default_repo.session = pretend.stub(
        get=lambda url, headers: response_with(
            status_code=200, _content=b'{"releases": {}}', _content_consumed=True
        ),
    )
    package = pretend.stub(safe_name="fake", metadata=pretend.stub(version="2.12.0"))

    assert default_repo.package_is_uploaded(package) is False


def test_package_is_uploaded_with_releases_using_cache(default_repo):
    """Return True when the package is in the releases cache."""
    default_repo._releases_json_data = {"fake": {"0.1": [{"filename": "fake.whl"}]}}
    package = pretend.stub(
        safe_name="fake",
        basefilename="fake.whl",
        metadata=pretend.stub(version="0.1"),
    )

    assert default_repo.package_is_uploaded(package) is True


def test_package_is_uploaded_with_releases_not_using_cache(default_repo):
    """Return True when the package is in the list of releases for a project."""
    default_repo.session = pretend.stub(
        get=lambda url, headers: response_with(
            status_code=200,
            _content=b'{"releases": {"0.1": [{"filename": "fake.whl"}]}}',
            _content_consumed=True,
        ),
    )
    package = pretend.stub(
        safe_name="fake",
        basefilename="fake.whl",
        metadata=pretend.stub(version="0.1"),
    )

    assert default_repo.package_is_uploaded(package, bypass_cache=True) is True


def test_package_is_uploaded_different_filenames(default_repo):
    """Return False when the package is not in the list of releases for a project."""
    default_repo.session = pretend.stub(
        get=lambda url, headers: response_with(
            status_code=200,
            _content=b'{"releases": {"0.1": [{"filename": "fake.whl"}]}}',
            _content_consumed=True,
        ),
    )
    package = pretend.stub(
        safe_name="fake",
        basefilename="foo.whl",
        metadata=pretend.stub(version="0.1"),
    )

    assert default_repo.package_is_uploaded(package) is False


def test_package_is_registered(default_repo):
    """Return API response from registering a package."""
    package = pretend.stub(
        basefilename="fake.whl", metadata_dictionary=lambda: {"name": "fake"}
    )

    resp = response_with(status_code=200)
    setattr(resp, "raw", pretend.stub())
    setattr(resp.raw, "close", lambda: None)
    default_repo.session = pretend.stub(
        post=lambda url, data, allow_redirects, headers: resp
    )

    assert default_repo.register(package)


@pytest.mark.parametrize("disable_progress_bar", [True, False])
def test_disable_progress_bar_is_forwarded_to_tqdm(
    monkeypatch, tmpdir, disable_progress_bar, default_repo
):
    """Toggle display of upload progress bar."""

    @contextmanager
    def progressbarstub(*args, **kwargs):
        assert "disable" in kwargs
        assert kwargs["disable"] == disable_progress_bar
        yield

    monkeypatch.setattr(repository, "ProgressBar", progressbarstub)
    default_repo.disable_progress_bar = disable_progress_bar

    default_repo.session = pretend.stub(
        post=lambda url, data, allow_redirects, headers: response_with(status_code=200)
    )

    fakefile = tmpdir.join("fake.whl")
    fakefile.write(".")

    def dictfunc():
        return {"name": "fake"}

    package = pretend.stub(
        safe_name="fake",
        metadata=pretend.stub(version="2.12.0"),
        basefilename="fake.whl",
        filename=str(fakefile),
        metadata_dictionary=dictfunc,
    )

    default_repo.upload(package)


def test_upload_retry(tmpdir, default_repo, capsys):
    """Print retry messages when the upload response indicates a server error."""
    default_repo.disable_progress_bar = True

    default_repo.session = pretend.stub(
        post=lambda url, data, allow_redirects, headers: response_with(
            status_code=500, reason="Internal server error"
        )
    )

    fakefile = tmpdir.join("fake.whl")
    fakefile.write(".")

    package = pretend.stub(
        safe_name="fake",
        metadata=pretend.stub(version="2.12.0"),
        basefilename="fake.whl",
        filename=str(fakefile),
        metadata_dictionary=lambda: {"name": "fake"},
    )

    # Upload with default max_redirects of 5
    default_repo.upload(package)

    msg = [
        (
            "Uploading fake.whl\n"
            'Received "500: Internal server error" '
            f"Package upload appears to have failed.  Retry {i} of 5"
        )
        for i in range(1, 6)
    ]

    captured = capsys.readouterr()
    assert captured.out == "\n".join(msg) + "\n"

    # Upload with custom max_redirects of 3
    default_repo.upload(package, 3)

    msg = [
        (
            "Uploading fake.whl\n"
            'Received "500: Internal server error" '
            f"Package upload appears to have failed.  Retry {i} of 3"
        )
        for i in range(1, 4)
    ]

    captured = capsys.readouterr()
    assert captured.out == "\n".join(msg) + "\n"


@pytest.mark.parametrize(
    "package_meta,repository_url,release_urls",
    [
        # Single package
        (
            [("fake", "2.12.0")],
            utils.DEFAULT_REPOSITORY,
            {"https://pypi.org/project/fake/2.12.0/"},
        ),
        # Single package to testpypi
        (
            [("fake", "2.12.0")],
            utils.TEST_REPOSITORY,
            {"https://test.pypi.org/project/fake/2.12.0/"},
        ),
        # Multiple packages (faking a wheel and an sdist)
        (
            [("fake", "2.12.0"), ("fake", "2.12.0")],
            utils.DEFAULT_REPOSITORY,
            {"https://pypi.org/project/fake/2.12.0/"},
        ),
        # Multiple releases
        (
            [("fake", "2.12.0"), ("fake", "2.12.1")],
            utils.DEFAULT_REPOSITORY,
            {
                "https://pypi.org/project/fake/2.12.0/",
                "https://pypi.org/project/fake/2.12.1/",
            },
        ),
        # Not pypi
        ([("fake", "2.12.0")], "http://devpi.example.com", set()),
        # No packages
        ([], utils.DEFAULT_REPOSITORY, set()),
    ],
)
def test_release_urls(package_meta, repository_url, release_urls):
    """Generate a set of PyPI release URLs for a list of packages."""
    packages = [
        pretend.stub(safe_name=name, metadata=pretend.stub(version=version))
        for name, version in package_meta
    ]

    repo = repository.Repository(
        repository_url=repository_url,
        username="username",
        password="password",
    )

    assert repo.release_urls(packages) == release_urls


def test_package_is_uploaded_incorrect_repo_url():
    """Return False when using an incorrect repository URL."""
    repo = repository.Repository(
        repository_url="https://bad.repo.com/legacy",
        username="username",
        password="password",
    )

    repo.url = "https://bad.repo.com/legacy"

    assert repo.package_is_uploaded(None) is False


@pytest.mark.parametrize(
    "username, password, messages",
    [
        (None, None, ["username: <empty>", "password: <empty>"]),
        ("", "", ["username: <empty>", "password: <empty>"]),
        ("username", "password", ["username: username", "password: <hidden>"]),
    ],
)
def test_logs_username_and_password(username, password, messages, caplog):
    caplog.set_level(logging.INFO, "twine")

    repository.Repository(
        repository_url=utils.DEFAULT_REPOSITORY,
        username=username,
        password=password,
    )

    assert caplog.messages == messages
