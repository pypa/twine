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
import pretend
import pytest
import requests

from twine import cli
from twine import commands
from twine import exceptions
from twine import package as package_file
from twine.commands import upload

from . import helpers

RELEASE_URL = "https://pypi.org/project/twine/1.5.0/"
NEW_RELEASE_URL = "https://pypi.org/project/twine/1.6.5/"


def test_successful_upload(make_settings, capsys):
    upload_settings = make_settings()

    stub_response = pretend.stub(
        is_redirect=False, status_code=201, raise_for_status=lambda: None
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response,
        close=lambda: None,
        release_urls=lambda packages: {RELEASE_URL, NEW_RELEASE_URL},
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(
        upload_settings,
        [
            helpers.WHEEL_FIXTURE,
            helpers.SDIST_FIXTURE,
            helpers.NEW_SDIST_FIXTURE,
            helpers.NEW_WHEEL_FIXTURE,
        ],
    )

    # A truthy result means the upload failed
    assert result is None

    captured = capsys.readouterr()
    assert captured.out.count(RELEASE_URL) == 1
    assert captured.out.count(NEW_RELEASE_URL) == 1


def test_successful_upload_add_gpg_signature(make_settings, capsys, monkeypatch):
    """Test uploading package when gpg signature are added to it"""

    # Create a custom package object and monkeypatch signed_basefilename attribute
    # with the gps signature file name
    package = package_file.PackageFile(
        filename=helpers.WHEEL_FIXTURE,
        comment=None,
        metadata=pretend.stub(name="twine"),
        python_version=None,
        filetype=None,
    )
    package.signed_basefilename = "twine.asc"

    # Patch from_filename to return our custom patched package
    monkeypatch.setattr(
        package_file.PackageFile, "from_filename", lambda filename, comment: package
    )

    # Create a call recorder to record calls to add_gpg_signature
    replaced_add_gpg_signature = pretend.call_recorder(
        lambda signature_filepath, signature_filename: None
    )
    monkeypatch.setattr(package, "add_gpg_signature", replaced_add_gpg_signature)

    # Patch _find_dists to return the provided list of dists along with gpg
    # signature file
    monkeypatch.setattr(
        commands,
        "_find_dists",
        lambda dists: [helpers.WHEEL_FIXTURE, "/foo/bar/twine.asc"],
    )

    upload_settings = make_settings()

    # Stub create_repository to mock successful upload of package
    stub_response = pretend.stub(
        is_redirect=False, status_code=201, raise_for_status=lambda: None
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response,
        close=lambda: None,
        release_urls=lambda packages: {RELEASE_URL, NEW_RELEASE_URL},
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, None)

    # A truthy result means the upload failed
    assert result is None

    captured = capsys.readouterr()
    assert captured.out.count(RELEASE_URL) == 1
    assert captured.out.count(NEW_RELEASE_URL) == 1
    args = ("/foo/bar/twine.asc", "twine.asc")
    assert replaced_add_gpg_signature.calls == [pretend.call(*args)]


def test_successful_upload_sign_package(make_settings, capsys, monkeypatch):
    """Test uploading package when package is signed"""

    # Create a custom package object
    package = package_file.PackageFile(
        filename=helpers.WHEEL_FIXTURE,
        comment=None,
        metadata=pretend.stub(name="twine"),
        python_version=None,
        filetype=None,
    )

    # Create a call recorder to record calls to package.sign
    replaced_sign = pretend.call_recorder(lambda sign_with, identity: None)
    monkeypatch.setattr(package, "sign", replaced_sign)

    # Patch from_filename to return our custom package
    monkeypatch.setattr(
        package_file.PackageFile, "from_filename", lambda filename, comment: package
    )

    # Update upload settings with attributes used to sign packages
    upload_settings = make_settings()
    upload_settings.sign = True
    upload_settings.sign_with = "gpg"
    upload_settings.identity = "identity"

    # Stub create_repository to mock successful upload of package
    stub_response = pretend.stub(
        is_redirect=False, status_code=201, raise_for_status=lambda: None
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response,
        close=lambda: None,
        release_urls=lambda packages: {RELEASE_URL, NEW_RELEASE_URL},
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])

    # A truthy result means the upload failed
    assert result is None

    captured = capsys.readouterr()
    assert captured.out.count(RELEASE_URL) == 1
    assert captured.out.count(NEW_RELEASE_URL) == 1
    args = ("gpg", "identity")
    assert replaced_sign.calls == [pretend.call(*args)]


@pytest.mark.parametrize("verbose", [False, True])
def test_exception_for_http_status(verbose, make_settings, capsys):
    upload_settings = make_settings()
    upload_settings.verbose = verbose

    stub_response = pretend.stub(
        is_redirect=False,
        status_code=403,
        text="Invalid or non-existent authentication information",
        raise_for_status=pretend.raiser(requests.HTTPError),
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response, close=lambda: None,
    )

    upload_settings.create_repository = lambda: stub_repository

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


def test_prints_skip_message_for_uploaded_package(make_settings, capsys):
    upload_settings = make_settings(skip_existing=True)

    stub_repository = pretend.stub(
        # Short-circuit the upload, so no need for a stub response
        package_is_uploaded=lambda package: True,
        release_urls=lambda packages: {},
        close=lambda: None,
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])

    # A truthy result means the upload failed
    assert result is None

    captured = capsys.readouterr()
    assert "Skipping twine-1.5.0-py2.py3-none-any.whl" in captured.out
    assert RELEASE_URL not in captured.out


def test_prints_skip_message_for_response(make_settings, capsys):
    upload_settings = make_settings(skip_existing=True)

    stub_response = pretend.stub(is_redirect=False, status_code=409,)

    stub_repository = pretend.stub(
        # Do the upload, triggering the error response
        package_is_uploaded=lambda package: False,
        release_urls=lambda packages: {},
        upload=lambda package: stub_response,
        close=lambda: None,
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, [helpers.WHEEL_FIXTURE])

    # A truthy result means the upload failed
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
def test_check_status_code_for_wrong_repo_url(repo_url, make_settings):
    upload_settings = make_settings()

    # override defaults to use incorrect URL
    upload_settings.repository_config["repository"] = repo_url

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
