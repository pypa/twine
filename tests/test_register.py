import pretend
import pytest

from twine import cli
from twine import exceptions
from twine.commands import register

from . import helpers


@pytest.fixture()
def register_settings(make_settings):
    """Return a factory function for settings.Settings for register."""
    return make_settings(
        """
        [pypi]
        repository: https://test.pypi.org/legacy/
        username:foo
        password:bar
        """
    )


def test_successful_register(register_settings):
    """Return a successful result for a valid repository url and package."""
    stub_response = pretend.stub(
        is_redirect=False,
        status_code=200,
        headers={"location": "https://test.pypi.org/legacy/"},
        raise_for_status=lambda: None,
    )

    stub_repository = pretend.stub(
        register=lambda package: stub_response, close=lambda: None
    )

    register_settings.create_repository = lambda: stub_repository

    result = register.register(register_settings, helpers.WHEEL_FIXTURE)

    assert result is None


def test_exception_for_redirect(register_settings):
    """Raise an exception when repository URL results in a redirect."""
    repository_url = register_settings.repository_config["repository"]
    redirect_url = "https://malicious.website.org/danger/"

    stub_response = pretend.stub(
        is_redirect=True,
        status_code=301,
        headers={"location": redirect_url},
    )

    stub_repository = pretend.stub(
        register=lambda package: stub_response, close=lambda: None
    )

    register_settings.create_repository = lambda: stub_repository

    with pytest.raises(
        exceptions.RedirectDetected,
        match=rf"{repository_url}.+{redirect_url}.+\nIf you trust these URLs",
    ):
        register.register(register_settings, helpers.WHEEL_FIXTURE)


def test_non_existent_package(register_settings):
    """Raise an exception when package file doesn't exist."""
    stub_repository = pretend.stub()

    register_settings.create_repository = lambda: stub_repository

    package = "/foo/bar/baz.whl"
    with pytest.raises(
        exceptions.PackageNotFound,
        match=f'"{package}" does not exist on the file system.',
    ):
        register.register(register_settings, package)


@pytest.mark.parametrize("repo", ["pypi", "testpypi"])
def test_values_from_env_pypi(monkeypatch, repo):
    """Use env vars for settings when run from command line."""

    def none_register(*args, **settings_kwargs):
        pass

    replaced_register = pretend.call_recorder(none_register)
    monkeypatch.setattr(register, "register", replaced_register)
    testenv = {
        "TWINE_REPOSITORY": repo,
        # Ignored because the TWINE_REPOSITORY is PyPI/TestPyPI
        "TWINE_USERNAME": "this-is-ignored",
        "TWINE_PASSWORD": "pypipassword",
        "TWINE_CERT": "/foo/bar.crt",
    }
    with helpers.set_env(**testenv):
        cli.dispatch(["register", helpers.WHEEL_FIXTURE])
    register_settings = replaced_register.calls[0].args[0]
    assert "pypipassword" == register_settings.password
    assert "__token__" == register_settings.username
    assert "/foo/bar.crt" == register_settings.cacert


def test_values_from_env_not_pypi(monkeypatch, write_config_file):
    """Use env vars for settings when run from command line."""
    write_config_file(
        """
        [distutils]
        index-servers =
            notpypi

        [notpypi]
        repository: https://upload.example.org/legacy/
        username:someusername
        password:password
        """
    )

    def none_register(*args, **settings_kwargs):
        pass

    replaced_register = pretend.call_recorder(none_register)
    monkeypatch.setattr(register, "register", replaced_register)
    testenv = {
        "TWINE_REPOSITORY": "notpypi",
        "TWINE_USERNAME": "someusername",
        "TWINE_PASSWORD": "pypipassword",
        "TWINE_CERT": "/foo/bar.crt",
    }
    with helpers.set_env(**testenv):
        cli.dispatch(["register", helpers.WHEEL_FIXTURE])
    register_settings = replaced_register.calls[0].args[0]
    assert "pypipassword" == register_settings.password
    assert "someusername" == register_settings.username
    assert "/foo/bar.crt" == register_settings.cacert
