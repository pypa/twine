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
from __future__ import unicode_literals

import textwrap

import pretend
import pytest

from twine.commands import upload
from twine import package, cli, exceptions, settings
import twine

import helpers

WHEEL_FIXTURE = 'tests/fixtures/twine-1.5.0-py2.py3-none-any.whl'


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


def test_successful_upload(make_settings):
    upload_settings = make_settings()

    stub_response = pretend.stub(
        is_redirect=False,
        status_code=201,
        raise_for_status=lambda: None
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response,
        close=lambda: None
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, [WHEEL_FIXTURE])

    # A truthy result means the upload failed
    assert result is None


def test_get_config_old_format(make_settings):
    try:
        make_settings("""
            [server-login]
            username:foo
            password:bar
        """)
    except KeyError as err:
        assert err.args[0] == (
            "Missing 'pypi' section from the configuration file\n"
            "or not a complete URL in --repository-url.\n"
            "Maybe you have a out-dated '{0}' format?\n"
            "more info: "
            "https://docs.python.org/distutils/packageindex.html#pypirc\n"
        ).format(pypirc)


def test_deprecated_repo(make_settings):
    with pytest.raises(exceptions.UploadToDeprecatedPyPIDetected) as err:
        upload_settings = make_settings("""
            [pypi]
            repository: https://pypi.python.org/pypi/
            username:foo
            password:bar
        """)

        upload.upload(upload_settings, [WHEEL_FIXTURE])

    assert err.value.args[0] == (
        "You're trying to upload to the legacy PyPI site "
        "'https://pypi.python.org/pypi/'. "
        "Uploading to those sites is deprecated. \n "
        "The new sites are pypi.org and test.pypi.org. Try using "
        "https://upload.pypi.org/legacy/ "
        "(or https://test.pypi.org/legacy/) "
        "to upload your packages instead. "
        "These are the default URLs for Twine now. \n "
        "More at "
        "https://packaging.python.org/guides/migrating-to-pypi-org/ ."
    )


def test_exception_for_redirect(make_settings):
    upload_settings = make_settings("""
        [pypi]
        repository: https://test.pypi.org/legacy
        username:foo
        password:bar
    """)

    stub_response = pretend.stub(
        is_redirect=True,
        status_code=301,
        headers={'location': 'https://test.pypi.org/legacy/'}
    )

    stub_repository = pretend.stub(
        upload=lambda package: stub_response,
        close=lambda: None
    )

    upload_settings.create_repository = lambda: stub_repository

    with pytest.raises(exceptions.RedirectDetected) as err:
        upload.upload(upload_settings, [WHEEL_FIXTURE])

    assert err.value.args[0] == (
        "Unexpected redirect from https://test.pypi.org/legacy"
        " to https://test.pypi.org/legacy/."
        "\nYou might need to change the configured repository URL."
        "\nAborting."
    )


def test_prints_skip_message_for_uploaded_package(make_settings, capsys):
    upload_settings = make_settings(skip_existing=True)

    stub_repository = pretend.stub(
        # Short-circuit the upload, so no need for a stub response
        package_is_uploaded=lambda package: True,
        close=lambda: None
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, [WHEEL_FIXTURE])

    # A truthy result means the upload failed
    assert result is None

    captured = capsys.readouterr()
    assert "Skipping twine-1.5.0-py2.py3-none-any.whl" in captured.out


def test_prints_skip_message_for_response(make_settings, capsys):
    upload_settings = make_settings(skip_existing=True)

    stub_response = pretend.stub(
        is_redirect=False,
        status_code=409,
    )

    stub_repository = pretend.stub(
        # Do the upload, triggering the error response
        package_is_uploaded=lambda package: False,
        upload=lambda package: stub_response,
        close=lambda: None
    )

    upload_settings.create_repository = lambda: stub_repository

    result = upload.upload(upload_settings, [WHEEL_FIXTURE])

    # A truthy result means the upload failed
    assert result is None

    captured = capsys.readouterr()
    assert "Skipping twine-1.5.0-py2.py3-none-any.whl" in captured.out


def test_skip_existing_skips_files_already_on_PyPI(monkeypatch):
    response = pretend.stub(
        status_code=400,
        reason='A file named "twine-1.5.0-py2.py3-none-any.whl" already '
               'exists for twine-1.5.0.')

    pkg = package.PackageFile.from_filename(WHEEL_FIXTURE, None)
    assert upload.skip_upload(response=response,
                              skip_existing=True,
                              package=pkg) is True


def test_skip_existing_skips_files_already_on_nexus(monkeypatch):
    # Nexus Repository Manager (https://www.sonatype.com/nexus-repository-oss)
    # responds with 400 when the file already exists
    response = pretend.stub(
        status_code=400,
        reason="Repository does not allow updating assets: pypi for url: "
               "http://www.foo.bar")

    pkg = package.PackageFile.from_filename(WHEEL_FIXTURE, None)
    assert upload.skip_upload(response=response,
                              skip_existing=True,
                              package=pkg) is True


def test_skip_existing_skips_files_already_on_pypiserver(monkeypatch):
    # pypiserver (https://pypi.org/project/pypiserver) responds with a
    # 409 when the file already exists.
    response = pretend.stub(
        status_code=409,
        reason='A file named "twine-1.5.0-py2.py3-none-any.whl" already '
               'exists for twine-1.5.0.')

    pkg = package.PackageFile.from_filename(WHEEL_FIXTURE, None)
    assert upload.skip_upload(response=response,
                              skip_existing=True,
                              package=pkg) is True


def test_skip_existing_skips_files_already_on_artifactory(monkeypatch):
    # Artifactory (https://jfrog.com/artifactory/) responds with 403
    # when the file already exists.
    response = pretend.stub(
        status_code=403,
        text="Not enough permissions to overwrite artifact "
             "'pypi-local:twine/1.5.0/twine-1.5.0-py2.py3-none-any.whl'"
             "(user 'twine-deployer' needs DELETE permission).")

    pkg = package.PackageFile.from_filename(WHEEL_FIXTURE, None)
    assert upload.skip_upload(response=response,
                              skip_existing=True,
                              package=pkg) is True


def test_skip_upload_respects_skip_existing(monkeypatch):
    response = pretend.stub(
        status_code=400,
        reason='A file named "twine-1.5.0-py2.py3-none-any.whl" already '
               'exists for twine-1.5.0.')

    pkg = package.PackageFile.from_filename(WHEEL_FIXTURE, None)
    assert upload.skip_upload(response=response,
                              skip_existing=False,
                              package=pkg) is False


def test_values_from_env(monkeypatch):
    def none_upload(*args, **settings_kwargs):
        pass

    replaced_upload = pretend.call_recorder(none_upload)
    monkeypatch.setattr(twine.commands.upload, "upload", replaced_upload)
    testenv = {"TWINE_USERNAME": "pypiuser",
               "TWINE_PASSWORD": "pypipassword",
               "TWINE_CERT": "/foo/bar.crt"}
    with helpers.set_env(**testenv):
        cli.dispatch(["upload", "path/to/file"])
    upload_settings = replaced_upload.calls[0].args[0]
    assert "pypipassword" == upload_settings.password
    assert "pypiuser" == upload_settings.username
    assert "/foo/bar.crt" == upload_settings.cacert
