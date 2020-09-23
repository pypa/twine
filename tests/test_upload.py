# Copyright 2014 Ian Cordasco
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
import os

import pretend
import pytest
import requests

from twine import cli
from twine import exceptions
from twine import package as package_file
from twine.commands import upload

from . import helpers

RELEASE_URL = "https://pypi.org/project/twine/1.5.0/"
NEW_RELEASE_URL = "https://pypi.org/project/twine/1.6.5/"


@pytest.fixture
def stub_response():
    """Mock successful upload of a package."""
    return pretend.stub(
        is_redirect=False, status_code=201, raise_for_status=lambda: None
    )


@pytest.fixture
def stub_repository(stub_response):
    """Allow assertions on the uploaded package."""
    return pretend.stub(
        upload=pretend.call_recorder(lambda package: stub_response),
        close=lambda: None,
        release_urls=lambda packages: set(),
    )


@pytest.fixture
def upload_settings(make_settings, stub_repository):
    """Use the stub repository when uploading."""
    upload_settings = make_settings()
    upload_settings.create_repository = lambda: stub_repository
    return upload_settings


def test_make_package_pre_signed_dist(upload_settings, capsys):
    """Create a PackageFile and print path, size, and user-provided signature."""
    filename = helpers.WHEEL_FIXTURE
    expected_size = "15.4 KB"
    signed_filename = helpers.WHEEL_FIXTURE + ".asc"
    signatures = {os.path.basename(signed_filename): signed_filename}

    upload_settings.sign = True
    upload_settings.verbose = True

    package = upload._make_package(filename, signatures, upload_settings)

    assert package.filename == filename
    assert package.gpg_signature is not None

    captured = capsys.readouterr()
    assert captured.out.count(f"{filename} ({expected_size})") == 1
    assert captured.out.count(f"Signed with {signed_filename}") == 1


def test_make_package_unsigned_dist(upload_settings, monkeypatch, capsys):
    """Create a PackageFile and print path, size, and Twine-generated signature."""
    filename = helpers.NEW_WHEEL_FIXTURE
    expected_size = "21.9 KB"
    signatures = {}

    upload_settings.sign = True
    upload_settings.verbose = True

    def stub_sign(package, *_):
        package.gpg_signature = (package.signed_basefilename, b"signature")

    monkeypatch.setattr(package_file.PackageFile, "sign", stub_sign)

    package = upload._make_package(filename, signatures, upload_settings)

    assert package.filename == filename
    assert package.gpg_signature is not None

    captured = capsys.readouterr()
    assert captured.out.count(f"{filename} ({expected_size})") == 1
    assert captured.out.count(f"Signed with {package.signed_filename}") == 1


def test_successs_prints_release_urls(upload_settings, stub_repository, capsys):
    """Print PyPI release URLS for each uploaded package."""
    stub_repository.release_urls = lambda packages: {RELEASE_URL, NEW_RELEASE_URL}

    result = upload.upload(
        upload_settings,
        [
            helpers.WHEEL_FIXTURE,
            helpers.SDIST_FIXTURE,
            helpers.NEW_SDIST_FIXTURE,
            helpers.NEW_WHEEL_FIXTURE,
        ],
    )
    assert result is None

    captured = capsys.readouterr()
    assert captured.out.count(RELEASE_URL) == 1
    assert captured.out.count(NEW_RELEASE_URL) == 1


def test_print_packages_if_verbose(upload_settings, capsys):
    """Print the path and file size of each distribution attempting to be uploaded."""
    dists_to_upload = {
        helpers.WHEEL_FIXTURE: "15.4 KB",
        helpers.SDIST_FIXTURE: "20.8 KB",
        helpers.NEW_SDIST_FIXTURE: "26.1 KB",
        helpers.NEW_WHEEL_FIXTURE: "21.9 KB",
    }

    upload_settings.verbose = True

    result = upload.upload(upload_settings, dists_to_upload.keys())
    assert result is None

    captured = capsys.readouterr()

    for filename, size in dists_to_upload.items():
        assert captured.out.count(f"{filename} ({size})") == 1


def test_success_with_pre_signed_distribution(upload_settings, stub_repository):
    """Add GPG signature provided by user to uploaded package."""
    # Upload a pre-signed distribution
    result = upload.upload(
        upload_settings, [helpers.WHEEL_FIXTURE, helpers.WHEEL_FIXTURE + ".asc"]
    )
    assert result is None

    # The signature shoud be added via package.add_gpg_signature()
    package = stub_repository.upload.calls[0].args[0]
    assert package.gpg_signature == (
        "twine-1.5.0-py2.py3-none-any.whl.asc",
        b"signature",
    )


def test_success_when_gpg_is_run(upload_settings, stub_repository, monkeypatch):
    """Add GPG signature generated by gpg command to uploaded package."""
    # Indicate that upload() should run_gpg() to generate the signature, which
    # we'll stub out to use WHEEL_FIXTURE + ".asc"
    upload_settings.sign = True
    upload_settings.sign_with = "gpg"
    monkeypatch.setattr(
        package_file.PackageFile,
        "run_gpg",
        pretend.call_recorder(lambda cls, gpg_args: None),
    )

    # Upload an unsigned distribution
    result = upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])
    assert result is None

    # The signature shoud be added via package.sign()
    package = stub_repository.upload.calls[0].args[0]
    assert len(package.run_gpg.calls) == 1
    assert helpers.WHEEL_FIXTURE in package.run_gpg.calls[0].args[1]
    assert package.gpg_signature == (
        "twine-1.5.0-py2.py3-none-any.whl.asc",
        b"signature",
    )


@pytest.mark.parametrize("verbose", [False, True])
def test_exception_for_http_status(verbose, upload_settings, stub_response, capsys):
    upload_settings.verbose = verbose

    stub_response.is_redirect = False
    stub_response.status_code = 403
    stub_response.text = "Invalid or non-existent authentication information"
    stub_response.raise_for_status = pretend.raiser(requests.HTTPError)

    with pytest.raises(requests.HTTPError):
        upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])

    captured = capsys.readouterr()
    assert RELEASE_URL not in captured.out

    if verbose:
        assert stub_response.text in captured.out
        assert "--verbose" not in captured.out
    else:
        assert stub_response.text not in captured.out
        assert "--verbose" in captured.out


def test_get_config_old_format(make_settings, pypirc):
    try:
        make_settings(
            """
            [server-login]
            username:foo
            password:bar
        """
        )
    except KeyError as err:
        assert all(
            text in err.args[0]
            for text in [
                "'pypi'",
                "--repository-url",
                pypirc,
                "https://docs.python.org/",
            ]
        )


def test_deprecated_repo(make_settings):
    with pytest.raises(exceptions.UploadToDeprecatedPyPIDetected) as err:
        upload_settings = make_settings(
            """
            [pypi]
            repository: https://pypi.python.org/pypi/
            username:foo
            password:bar
        """
        )

        upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])

    assert all(
        text in err.value.args[0]
        for text in [
            "https://pypi.python.org/pypi/",
            "https://upload.pypi.org/legacy/",
            "https://test.pypi.org/legacy/",
            "https://packaging.python.org/",
        ]
    )


def test_exception_for_redirect(make_settings):
    # Not using fixtures because this setup is significantly different

    upload_settings = make_settings(
        """
        [pypi]
        repository: https://test.pypi.org/legacy
        username:foo
        password:bar
    """
    )

    stub_response = pretend.stub(
        is_redirect=True,
        status_code=301,
        headers={"location": "https://test.pypi.org/legacy/"},
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response, close=lambda: None
    )

    upload_settings.create_repository = lambda: stub_repository

    with pytest.raises(exceptions.RedirectDetected) as err:
        upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])

    assert "https://test.pypi.org/legacy/" in err.value.args[0]


def test_prints_skip_message_for_uploaded_package(
    upload_settings, stub_repository, capsys
):
    upload_settings.skip_existing = True

    # Short-circuit the upload
    stub_repository.package_is_uploaded = lambda package: True

    result = upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])
    assert result is None

    captured = capsys.readouterr()
    assert "Skipping twine-1.5.0-py2.py3-none-any.whl" in captured.out
    assert RELEASE_URL not in captured.out


def test_prints_skip_message_for_response(
    upload_settings, stub_response, stub_repository, capsys
):
    upload_settings.skip_existing = True

    stub_response.status_code = 409

    # Do the upload, triggering the error response
    stub_repository.package_is_uploaded = lambda package: False

    result = upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])
    assert result is None

    captured = capsys.readouterr()
    assert "Skipping twine-1.5.0-py2.py3-none-any.whl" in captured.out
    assert RELEASE_URL not in captured.out


@pytest.mark.parametrize(
    "response_kwargs",
    [
        pytest.param(
            dict(
                status_code=400,
                reason=(
                    'A file named "twine-1.5.0-py2.py3-none-any.whl" already '
                    "exists for twine-1.5.0."
                ),
            ),
            id="pypi",
        ),
        pytest.param(
            dict(
                status_code=400,
                reason=(
                    "Repository does not allow updating assets: pypi for url: "
                    "http://www.foo.bar"
                ),
            ),
            id="nexus",
        ),
        pytest.param(
            dict(
                status_code=400,
                text=(
                    '<div class="content-section">\n'
                    "    Repository does not allow updating assets: pypi-local\n"
                    "</div>\n"
                ),
            ),
            id="nexus_new",
        ),
        pytest.param(
            dict(
                status_code=409,
                reason=(
                    'A file named "twine-1.5.0-py2.py3-none-any.whl" already '
                    "exists for twine-1.5.0."
                ),
            ),
            id="pypiserver",
        ),
        pytest.param(
            dict(
                status_code=403,
                text=(
                    "Not enough permissions to overwrite artifact "
                    "'pypi-local:twine/1.5.0/twine-1.5.0-py2.py3-none-any.whl'"
                    "(user 'twine-deployer' needs DELETE permission)."
                ),
            ),
            id="artifactory_old",
        ),
        pytest.param(
            dict(
                status_code=403,
                text=(
                    "Not enough permissions to delete/overwrite artifact "
                    "'pypi-local:twine/1.5.0/twine-1.5.0-py2.py3-none-any.whl'"
                    "(user 'twine-deployer' needs DELETE permission)."
                ),
            ),
            id="artifactory_new",
        ),
        pytest.param(
            dict(
                status_code=400,
                text=(
                    '{"message":"validation failed: file name has already been taken"}'
                ),
            ),
            id="gitlab_enterprise",
        ),
    ],
)
def test_skip_existing_skips_files_on_repository(response_kwargs):
    assert upload.skip_upload(
        response=pretend.stub(**response_kwargs),
        skip_existing=True,
        package=package_file.PackageFile.from_filename(helpers.WHEEL_FIXTURE, None),
    )


@pytest.mark.parametrize(
    "response_kwargs",
    [
        pytest.param(
            dict(status_code=400, reason="Invalid credentials"), id="wrong_reason"
        ),
        pytest.param(dict(status_code=404), id="wrong_code"),
    ],
)
def test_skip_upload_doesnt_match(response_kwargs):
    assert not upload.skip_upload(
        response=pretend.stub(**response_kwargs),
        skip_existing=True,
        package=package_file.PackageFile.from_filename(helpers.WHEEL_FIXTURE, None),
    )


def test_skip_upload_respects_skip_existing():
    assert not upload.skip_upload(
        response=pretend.stub(),
        skip_existing=False,
        package=package_file.PackageFile.from_filename(helpers.WHEEL_FIXTURE, None),
    )


def test_values_from_env(monkeypatch):
    def none_upload(*args, **settings_kwargs):
        pass

    replaced_upload = pretend.call_recorder(none_upload)
    monkeypatch.setattr(upload, "upload", replaced_upload)
    testenv = {
        "TWINE_USERNAME": "pypiuser",
        "TWINE_PASSWORD": "pypipassword",
        "TWINE_CERT": "/foo/bar.crt",
    }
    with helpers.set_env(**testenv):
        cli.dispatch(["upload", "path/to/file"])
    upload_settings = replaced_upload.calls[0].args[0]
    assert "pypipassword" == upload_settings.password
    assert "pypiuser" == upload_settings.username
    assert "/foo/bar.crt" == upload_settings.cacert


@pytest.mark.parametrize(
    "repo_url",
    ["https://upload.pypi.org/", "https://test.pypi.org/", "https://pypi.org/"],
)
def test_check_status_code_for_wrong_repo_url(repo_url, upload_settings, stub_response):
    upload_settings.repository_config["repository"] = repo_url

    stub_response.url = repo_url
    stub_response.status_code = 405

    with pytest.raises(exceptions.InvalidPyPIUploadURL):
        upload.upload(
            upload_settings,
            [
                helpers.WHEEL_FIXTURE,
                helpers.SDIST_FIXTURE,
                helpers.NEW_SDIST_FIXTURE,
                helpers.NEW_WHEEL_FIXTURE,
            ],
        )
