# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import sys
import os.path
import textwrap

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

import pytest

from twine import utils

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


def test_get_config_missing(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    assert utils.get_config(pypirc) == {
        "pypi": {
            "repository": utils.DEFAULT_REPOSITORY,
            "username": None,
            "password": None,
        },
        "pypitest": {
            "repository": utils.TEST_REPOSITORY,
            "username": None,
            "password": None
        },
    }


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
            "username": 'testusername',
            "password": 'testpassword',
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

    monkeypatch.setitem(sys.modules, 'keyring', MockKeyring)

    pw = utils.get_password('system', 'user', None, {})
    assert pw == 'user@system sekure pa55word'


def test_get_password_keyring_defers_to_prompt(monkeypatch):
    monkeypatch.setattr(utils, 'password_prompt', lambda prompt: 'entered pw')

    class MockKeyring:
        @staticmethod
        def get_password(system, user):
            return

    monkeypatch.setitem(sys.modules, 'keyring', MockKeyring)

    pw = utils.get_password('system', 'user', None, {})
    assert pw == 'entered pw'


@pytest.fixture
def keyring_missing(monkeypatch):
    """
    Simulate that 'import keyring' raises an ImportError
    """
    real_import = builtins.__import__

    def my_import(name, *args, **kwargs):
        if name == 'keyring':
            raise ImportError
        return real_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', my_import)


@pytest.fixture
def entered_password(monkeypatch):
    monkeypatch.setattr(utils, 'password_prompt', lambda prompt: 'entered pw')


def test_get_password_keyring_missing_prompts(
        entered_password, keyring_missing):
    assert utils.get_password('system', 'user', None, {}) == 'entered pw'


@pytest.fixture
def keyring_no_backends(monkeypatch):
    """
    Simulate that keyring has no available backends. When keyring
    has no backends for the system, the backend will be a
    fail.Keyring, which raises RuntimeError on get_password.
    """
    class FailKeyring(object):
        @staticmethod
        def get_password(system, username):
            raise RuntimeError("fail!")
    monkeypatch.setitem(sys.modules, 'keyring', FailKeyring())


def test_get_password_runtime_error_suppressed(
        entered_password, keyring_no_backends, recwarn):
    assert utils.get_password('system', 'user', None, {}) == 'entered pw'
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert 'fail!' in str(warning)
