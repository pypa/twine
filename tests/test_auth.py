import pytest

from twine import auth
from twine import exceptions
from twine import utils

cred = auth.CredentialInput


@pytest.fixture
def config() -> utils.RepositoryConfig:
    return dict(repository="system")


def test_get_password_keyring_overrides_prompt(monkeypatch, config):
    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return "{user}@{system} sekure pa55word".format(**locals())

    monkeypatch.setattr(auth, "keyring", MockKeyring)

    pw = auth.Resolver(config, cred("user")).password
    assert pw == "user@system sekure pa55word"


def test_get_password_keyring_defers_to_prompt(monkeypatch, entered_password, config):
    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return

    monkeypatch.setattr(auth, "keyring", MockKeyring)

    pw = auth.Resolver(config, cred("user")).password
    assert pw == "entered pw"


def test_no_password_defers_to_prompt(monkeypatch, entered_password, config):
    config.update(password=None)
    pw = auth.Resolver(config, cred("user")).password
    assert pw == "entered pw"


def test_empty_password_bypasses_prompt(monkeypatch, entered_password, config):
    config.update(password="")
    pw = auth.Resolver(config, cred("user")).password
    assert pw == ""


def test_no_username_non_interactive_aborts(config):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, cred("user")).password


def test_no_password_non_interactive_aborts(config):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, cred("user")).password


def test_get_username_and_password_keyring_overrides_prompt(monkeypatch, config):
    class MockKeyring:
        @staticmethod
        def get_credential(system, user):
            return cred(
                "real_user", "real_user@{system} sekure pa55word".format(**locals())
            )

        @staticmethod
        def get_password(system, user):
            cred = MockKeyring.get_credential(system, user)
            if user != cred.username:
                raise RuntimeError("unexpected username")
            return cred.password

    monkeypatch.setattr(auth, "keyring", MockKeyring)

    res = auth.Resolver(config, cred())
    assert res.username == "real_user"
    assert res.password == "real_user@system sekure pa55word"


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
    assert auth.Resolver(config, cred()).username == "entered user"


def test_get_username_keyring_missing_non_interactive_aborts(
    entered_username, keyring_missing_get_credentials, config
):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, cred()).username


def test_get_password_keyring_missing_non_interactive_aborts(
    entered_username, keyring_missing_get_credentials, config
):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(config, cred("user")).password


@pytest.fixture
def keyring_no_backends(monkeypatch):
    """Simulate missing keyring backend raising RuntimeError on get_password."""

    class FailKeyring:
        @staticmethod
        def get_password(system, username):
            raise RuntimeError("fail!")

    monkeypatch.setattr(auth, "keyring", FailKeyring())


@pytest.fixture
def keyring_no_backends_get_credential(monkeypatch):
    """Simulate missing keyring backend raising RuntimeError on get_credential."""

    class FailKeyring:
        @staticmethod
        def get_credential(system, username):
            raise RuntimeError("fail!")

    monkeypatch.setattr(auth, "keyring", FailKeyring())


def test_get_username_runtime_error_suppressed(
    entered_username, keyring_no_backends_get_credential, recwarn, config
):
    assert auth.Resolver(config, cred()).username == "entered user"
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert "fail!" in str(warning)


def test_get_password_runtime_error_suppressed(
    entered_password, keyring_no_backends, recwarn, config
):
    assert auth.Resolver(config, cred("user")).password == "entered pw"
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert "fail!" in str(warning)


def test_get_username_return_none(entered_username, monkeypatch, config):
    """Prompt for username when it's not in keyring."""

    class FailKeyring:
        @staticmethod
        def get_credential(system, username):
            return None

    monkeypatch.setattr(auth, "keyring", FailKeyring())
    assert auth.Resolver(config, cred()).username == "entered user"
