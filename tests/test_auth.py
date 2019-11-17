import pytest
import munch

from twine import (
    auth,
    exceptions,
    types,
)


cred = types.CredentialInput.new


@pytest.fixture
def settings():
    return munch.Munch(
        repository_config={},
        system='system',
    )


def test_get_password_keyring_overrides_prompt(monkeypatch, settings):
    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return '{user}@{system} sekure pa55word'.format(**locals())

    monkeypatch.setattr(auth, 'keyring', MockKeyring)

    pw = auth.Resolver(settings, cred('user')).password
    assert pw == 'user@system sekure pa55word'


def test_get_password_keyring_defers_to_prompt(
        monkeypatch, entered_password, settings):
    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return

    monkeypatch.setattr(auth, 'keyring', MockKeyring)

    pw = auth.Resolver(settings, cred('user')).password
    assert pw == 'entered pw'


def test_no_password_defers_to_prompt(monkeypatch, entered_password, settings):
    settings.repository_config.update(password=None)
    pw = auth.Resolver(settings, cred('user')).password
    assert pw == 'entered pw'


def test_empty_password_bypasses_prompt(
        monkeypatch, entered_password, settings):
    settings.repository_config.update(password='')
    pw = auth.Resolver(settings, cred('user')).password
    assert pw == ''


def test_no_username_non_interactive_aborts(settings):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(settings, cred('user')).password


def test_no_password_non_interactive_aborts(settings):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(settings, cred('user')).password


def test_get_username_and_password_keyring_overrides_prompt(
        monkeypatch, settings):

    class MockKeyring:
        @staticmethod
        def get_credential(system, user):
            return cred(
                'real_user',
                'real_user@{system} sekure pa55word'.format(**locals())
            )

        @staticmethod
        def get_password(system, user):
            cred = MockKeyring.get_credential(system, user)
            if user != cred.username:
                raise RuntimeError("unexpected username")
            return cred.password

    monkeypatch.setattr(auth, 'keyring', MockKeyring)

    res = auth.Resolver(settings, cred())
    assert res.username == 'real_user'
    assert res.password == 'real_user@system sekure pa55word'


@pytest.fixture
def keyring_missing_get_credentials(monkeypatch):
    """
    Simulate keyring prior to 15.2 that does not have the
    'get_credential' API.
    """
    monkeypatch.delattr(auth.keyring, 'get_credential')


@pytest.fixture
def entered_username(monkeypatch):
    monkeypatch.setattr(
        auth, 'input', lambda prompt: 'entered user', raising=False)


@pytest.fixture
def entered_password(monkeypatch):
    monkeypatch.setattr(auth.getpass, 'getpass', lambda prompt: 'entered pw')


def test_get_username_keyring_missing_get_credentials_prompts(
        entered_username, keyring_missing_get_credentials, settings):
    assert auth.Resolver(settings, cred()).username == 'entered user'


def test_get_username_keyring_missing_non_interactive_aborts(
        entered_username, keyring_missing_get_credentials, settings):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(settings, cred()).username


def test_get_password_keyring_missing_non_interactive_aborts(
        entered_username, keyring_missing_get_credentials, settings):
    with pytest.raises(exceptions.NonInteractive):
        auth.Private(settings, cred('user')).password


@pytest.fixture
def keyring_no_backends(monkeypatch):
    """
    Simulate that keyring has no available backends. When keyring
    has no backends for the system, the backend will be a
    fail.Keyring, which raises RuntimeError on get_password.
    """
    class FailKeyring:
        @staticmethod
        def get_password(system, username):
            raise RuntimeError("fail!")
    monkeypatch.setattr(auth, 'keyring', FailKeyring())


@pytest.fixture
def keyring_no_backends_get_credential(monkeypatch):
    """
    Simulate that keyring has no available backends. When keyring
    has no backends for the system, the backend will be a
    fail.Keyring, which raises RuntimeError on get_credential.
    """
    class FailKeyring:
        @staticmethod
        def get_credential(system, username):
            raise RuntimeError("fail!")
    monkeypatch.setattr(auth, 'keyring', FailKeyring())


def test_get_username_runtime_error_suppressed(
        entered_username, keyring_no_backends_get_credential, recwarn,
        settings):
    assert auth.Resolver(settings, cred()).username == 'entered user'
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert 'fail!' in str(warning)


def test_get_password_runtime_error_suppressed(
        entered_password, keyring_no_backends, recwarn, settings):
    assert auth.Resolver(settings, cred('user')).password == 'entered pw'
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert 'fail!' in str(warning)
