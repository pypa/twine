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
import textwrap

import pytest
import pretend

from twine import exceptions, utils

import helpers


def test_get_config(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [distutils]
            index-servers = pypi

            [pypi]
            username = testuser
            password = testpassword
        """))

    assert utils.get_config(pypirc) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": "testuser",
            "password": "testpassword",
        },
    }


def test_get_config_no_distutils(tmpdir):
    """
    Even if the user hasn't set PyPI has an index server
    in 'index-servers', default to uploading to PyPI.
    """
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [pypi]
            username = testuser
            password = testpassword
        """))

    assert utils.get_config(pypirc) == {
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


def test_get_config_no_section(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [distutils]
            index-servers = pypi foo

            [pypi]
            username = testuser
            password = testpassword
        """))

    assert utils.get_config(pypirc) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": "testuser",
            "password": "testpassword",
        },
    }


def test_get_config_override_pypi_url(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [pypi]
            repository = http://pypiproxy
        """))

    assert utils.get_config(pypirc)['pypi']['repository'] == 'http://pypiproxy'


def test_get_config_missing(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    assert utils.get_config(pypirc) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": None,
            "password": None,
        },
        "testpypi": {
            "repository": utils.TEST_REPOSITORY,
            "username": None,
            "password": None
        },
    }


def test_empty_userpass(tmpdir):
    """
    Empty username and password may be supplied to suppress
    prompts. See #426.
    """
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [pypi]
            username=
            password=
        """))

    config = utils.get_config(pypirc)
    pypi = config['pypi']

    assert pypi['username'] == pypi['password'] == ''


def test_get_repository_config_missing(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    repository_url = "https://notexisting.python.org/pypi"
    exp = {
        "repository": repository_url,
        "username": None,
        "password": None,
    }
    assert (utils.get_repository_from_config(pypirc, 'foo', repository_url) ==
            exp)
    assert (utils.get_repository_from_config(pypirc, 'pypi', repository_url) ==
            exp)
    exp = {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": None,
            "password": None,
        }
    assert utils.get_repository_from_config(pypirc, "pypi") == exp


def test_get_config_deprecated_pypirc():
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    deprecated_pypirc_path = os.path.join(tests_dir, 'fixtures',
                                          'deprecated-pypirc')

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
    ('cli_value', 'config', 'key', 'strategy', 'expected'),
    (
        ('cli', {}, 'key', lambda: 'fallback', 'cli'),
        (None, {'key': 'value'}, 'key', lambda: 'fallback', 'value'),
        (None, {}, 'key', lambda: 'fallback', 'fallback'),
    ),
)
def test_get_userpass_value(cli_value, config, key, strategy, expected):
    ret = utils.get_userpass_value(cli_value, config, key, strategy)
    assert ret == expected


@pytest.mark.parametrize(
    ('env_name', 'default', 'environ', 'expected'),
    [
        ('MY_PASSWORD', None, {}, None),
        ('MY_PASSWORD', None, {'MY_PASSWORD': 'foo'}, 'foo'),
        ('URL', 'https://example.org', {}, 'https://example.org'),
        ('URL', 'https://example.org', {'URL': 'https://pypi.org'},
            'https://pypi.org'),
    ],
)
def test_default_to_environment_action(env_name, default, environ, expected):
    option_strings = ('-x', '--example')
    dest = 'example'
    with helpers.set_env(**environ):
        action = utils.EnvironmentDefault(
            env=env_name,
            default=default,
            option_strings=option_strings,
            dest=dest,
        )
    assert action.env == env_name
    assert action.default == expected


def test_get_password_keyring_overrides_prompt(monkeypatch):
    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return '{user}@{system} sekure pa55word'.format(**locals())

    monkeypatch.setattr(utils, 'keyring', MockKeyring)

    pw = utils.get_password('system', 'user', None, {})
    assert pw == 'user@system sekure pa55word'


def test_get_password_keyring_defers_to_prompt(monkeypatch):
    monkeypatch.setattr(utils, 'password_prompt', lambda prompt: 'entered pw')

    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return

    monkeypatch.setattr(utils, 'keyring', MockKeyring)

    pw = utils.get_password('system', 'user', None, {})
    assert pw == 'entered pw'


def test_no_password_defers_to_prompt(monkeypatch):
    monkeypatch.setattr(utils, 'password_prompt', lambda prompt: 'entered pw')
    pw = utils.get_password('system', 'user', None, {'password': None})
    assert pw == 'entered pw'


def test_empty_password_bypasses_prompt(monkeypatch):
    monkeypatch.setattr(utils, 'password_prompt', lambda prompt: 'entered pw')
    pw = utils.get_password('system', 'user', None, {'password': ''})
    assert pw == ''


def test_no_username_non_interactive_aborts():
    with pytest.raises(exceptions.NonInteractive):
        utils.get_username('system', None, {'username': None}, True)


def test_no_password_non_interactive_aborts():
    with pytest.raises(exceptions.NonInteractive):
        utils.get_password('system', 'user', None, {'password': None}, True)


def test_get_username_and_password_keyring_overrides_prompt(monkeypatch):
    import collections
    Credential = collections.namedtuple('Credential', 'username password')

    class MockKeyring:
        @staticmethod
        def get_credential(system, user):
            return Credential(
                'real_user',
                'real_user@{system} sekure pa55word'.format(**locals())
            )

        @staticmethod
        def get_password(system, user):
            cred = MockKeyring.get_credential(system, user)
            if user != cred.username:
                raise RuntimeError("unexpected username")
            return cred.password

    monkeypatch.setattr(utils, 'keyring', MockKeyring)

    user = utils.get_username('system', None, {})
    assert user == 'real_user'
    pw = utils.get_password('system', user, None, {})
    assert pw == 'real_user@system sekure pa55word'


@pytest.fixture
def keyring_missing_get_credentials(monkeypatch):
    """
    Simulate keyring prior to 15.2 that does not have the
    'get_credential' API.
    """
    monkeypatch.delattr(utils.keyring, 'get_credential')


@pytest.fixture
def entered_username(monkeypatch):
    monkeypatch.setattr(utils, 'input_func', lambda prompt: 'entered user')


@pytest.fixture
def entered_password(monkeypatch):
    monkeypatch.setattr(utils, 'password_prompt', lambda prompt: 'entered pw')


def test_get_username_keyring_missing_get_credentials_prompts(
        entered_username, keyring_missing_get_credentials):
    assert utils.get_username('system', None, {}) == 'entered user'


def test_get_username_keyring_missing_non_interactive_aborts(
        entered_username, keyring_missing_get_credentials):
    with pytest.raises(exceptions.NonInteractive):
        utils.get_username('system', None, {}, True)


def test_get_password_keyring_missing_non_interactive_aborts(
        entered_username, keyring_missing_get_credentials):
    with pytest.raises(exceptions.NonInteractive):
        utils.get_password('system', 'user', None, {}, True)


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
    monkeypatch.setattr(utils, 'keyring', FailKeyring())


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
    monkeypatch.setattr(utils, 'keyring', FailKeyring())


def test_get_username_runtime_error_suppressed(
        entered_username, keyring_no_backends_get_credential, recwarn):
    assert utils.get_username('system', None, {}) == 'entered user'
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert 'fail!' in str(warning)


def test_get_password_runtime_error_suppressed(
        entered_password, keyring_no_backends, recwarn):
    assert utils.get_password('system', 'user', None, {}) == 'entered pw'
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert 'fail!' in str(warning)


@pytest.mark.parametrize('repo_url', [
    "https://pypi.python.org",
    "https://testpypi.python.org"
])
def test_check_status_code_for_deprecated_pypi_url(repo_url):
    response = pretend.stub(
        status_code=410,
        url=repo_url
    )

    # value of Verbose doesn't matter for this check
    with pytest.raises(exceptions.UploadToDeprecatedPyPIDetected):
        utils.check_status_code(response, False)
