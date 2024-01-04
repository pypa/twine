import getpass
import logging
import re

import pytest

from twine import auth
from twine import exceptions
from twine import utils


@pytest.fixture
def config() -> utils.RepositoryConfig:
    return dict(repository="system")


def test_get_username_keyring_defers_to_prompt(monkeypatch, entered_username, config):
    class MockKeyring:
        @staticmethod
        def get_credential(system, user):
            return None

    monkeypatch.setattr(auth, "keyring", MockKeyring)

    username = auth.Resolver(config, auth.CredentialInput()).username
    assert username == "entered user"


def test_get_password_keyring_defers_to_prompt(monkeypatch, entered_password, config):
    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return None

    monkeypatch.setattr(auth, "keyring", MockKeyring)

    pw = auth.Resolver(config, auth.CredentialInput("user")).password
    assert pw == "entered pw"


def test_no_password_defers_to_prompt(monkeypatch, entered_password, config):
    config.update(password=None)
    pw = auth.Resolver(config, auth.CredentialInput("user")).password
    assert pw == "entered pw"


def test_empty_password_bypasses_prompt(monkeypatch, entered_password, config):
    config.update(password="")
    pw = auth.Resolver(config, auth.CredentialInput("user")).password
    assert pw == ""


def test_no_username_non_interactive_aborts(config):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, auth.CredentialInput()).username


def test_no_password_non_interactive_aborts(config):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, auth.CredentialInput("user")).password


def test_get_username_and_password_keyring_overrides_prompt(
    monkeypatch, config, caplog
):
    caplog.set_level(logging.INFO, "twine")

    class MockKeyring:
        @staticmethod
        def get_credential(system, user):
            return auth.CredentialInput(
                "real_user", f"real_user@{system} sekure pa55word"
            )

        @staticmethod
        def get_password(system, user):
            cred = MockKeyring.get_credential(system, user)
            if user != cred.username:
                raise RuntimeError("unexpected username")
            return cred.password

    monkeypatch.setattr(auth, "keyring", MockKeyring)

    res = auth.Resolver(config, auth.CredentialInput())

    assert res.username == "real_user"
    assert res.password == "real_user@system sekure pa55word"

    assert caplog.messages == [
        "Querying keyring for username",
        "username set from keyring",
        "Querying keyring for password",
        "password set from keyring",
    ]


@pytest.fixture
def keyring_missing_get_credentials(monkeypatch):
    """Simulate keyring prior to 15.2 that does not have the 'get_credential' API."""
    monkeypatch.delattr(auth.keyring, "get_credential")


@pytest.fixture
def entered_username(monkeypatch):
    monkeypatch.setattr(auth, "input", lambda prompt: "entered user", raising=False)


def test_get_username_keyring_missing_get_credentials_prompts(
    entered_username, keyring_missing_get_credentials, config
):
    assert auth.Resolver(config, auth.CredentialInput()).username == "entered user"


def test_get_username_keyring_missing_non_interactive_aborts(
    entered_username, keyring_missing_get_credentials, config
):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, auth.CredentialInput()).username


def test_get_password_keyring_missing_non_interactive_aborts(
    entered_username, keyring_missing_get_credentials, config
):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, auth.CredentialInput("user")).password


def test_get_username_keyring_runtime_error_logged(
    entered_username, monkeypatch, config, caplog
):
    class FailKeyring:
        """Simulate missing keyring backend raising RuntimeError on get_credential."""

        @staticmethod
        def get_credential(system, username):
            raise RuntimeError("fail!")

    monkeypatch.setattr(auth, "keyring", FailKeyring)

    assert auth.Resolver(config, auth.CredentialInput()).username == "entered user"

    assert re.search(
        r"Error getting username from keyring.+Traceback.+RuntimeError: fail!",
        caplog.text,
        re.DOTALL,
    )


def test_get_password_keyring_runtime_error_logged(
    entered_username, entered_password, monkeypatch, config, caplog
):
    class FailKeyring:
        """Simulate missing keyring backend raising RuntimeError on get_password."""

        @staticmethod
        def get_password(system, username):
            raise RuntimeError("fail!")

    monkeypatch.setattr(auth, "keyring", FailKeyring)

    assert auth.Resolver(config, auth.CredentialInput()).password == "entered pw"

    assert re.search(
        r"Error getting password from keyring.+Traceback.+RuntimeError: fail!",
        caplog.text,
        re.DOTALL,
    )


def _raise_home_key_error():
    """Simulate environment from https://github.com/pypa/twine/issues/889."""
    try:
        raise KeyError("HOME")
    except KeyError:
        raise KeyError("uid not found: 999")


def test_get_username_keyring_key_error_logged(
    entered_username, monkeypatch, config, caplog
):
    class FailKeyring:
        @staticmethod
        def get_credential(system, username):
            _raise_home_key_error()

    monkeypatch.setattr(auth, "keyring", FailKeyring)

    assert auth.Resolver(config, auth.CredentialInput()).username == "entered user"

    assert re.search(
        r"Error getting username from keyring"
        r".+Traceback"
        r".+KeyError: 'HOME'"
        r".+KeyError: 'uid not found: 999'",
        caplog.text,
        re.DOTALL,
    )


def test_get_password_keyring_key_error_logged(
    entered_username, entered_password, monkeypatch, config, caplog
):
    class FailKeyring:
        @staticmethod
        def get_password(system, username):
            _raise_home_key_error()

    monkeypatch.setattr(auth, "keyring", FailKeyring)

    assert auth.Resolver(config, auth.CredentialInput()).password == "entered pw"

    assert re.search(
        r"Error getting password from keyring"
        r".+Traceback"
        r".+KeyError: 'HOME'"
        r".+KeyError: 'uid not found: 999'",
        caplog.text,
        re.DOTALL,
    )


def test_logs_cli_values(caplog, config):
    caplog.set_level(logging.INFO, "twine")

    res = auth.Resolver(config, auth.CredentialInput("username", "password"))

    assert res.username == "username"
    assert res.password == "password"

    assert caplog.messages == [
        "username set by command options",
        "password set by command options",
    ]


def test_logs_config_values(config, caplog):
    caplog.set_level(logging.INFO, "twine")

    config.update(username="username", password="password")
    res = auth.Resolver(config, auth.CredentialInput())

    assert res.username == "username"
    assert res.password == "password"

    assert caplog.messages == [
        "username set from config file",
        "password set from config file",
    ]


@pytest.mark.parametrize(
    "password, warning",
    [
        ("", "Your password is empty"),
        ("\x16", "Your password contains control characters"),
        ("entered\x16pw", "Your password contains control characters"),
    ],
)
def test_warns_for_empty_password(
    password,
    warning,
    monkeypatch,
    entered_username,
    config,
    caplog,
):
    # Avoiding additional warning "No recommended backend was available"
    monkeypatch.setattr(auth.keyring, "get_password", lambda system, user: None)

    monkeypatch.setattr(getpass, "getpass", lambda prompt: password)

    assert auth.Resolver(config, auth.CredentialInput()).password == password

    assert caplog.messages[0].startswith(warning)
