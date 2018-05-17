"""Tests for the Settings class and module."""
# Copyright 2018 Ian Stapleton Cordasco
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
from __future__ import unicode_literals

from twine import exceptions
from twine import settings

import pretend
import pytest


def test_settings_takes_no_positional_arguments():
    """Verify that the Settings initialization is kw-only."""
    with pytest.raises(TypeError):
        settings.Settings('a', 'b', 'c')


def test_settings_transforms_config(monkeypatch):
    """Verify that the settings object transforms the passed in options."""
    replaced_get_repository_from_config = pretend.call_recorder(
        lambda *args: {'repository': 'https://upload.pypi.org/legacy/'}
    )
    monkeypatch.setattr(settings.utils, 'get_repository_from_config',
                        replaced_get_repository_from_config)
    replaced_normalize_repository_url = pretend.call_recorder(
        lambda *args: 'https://upload.pypi.org/legacy/'
    )
    monkeypatch.setattr(settings.utils, 'normalize_repository_url',
                        replaced_normalize_repository_url)
    replaced_get_username = pretend.call_recorder(
        lambda *args: 'username'
    )
    monkeypatch.setattr(settings.utils, 'get_username',
                        replaced_get_username)
    replaced_get_password = pretend.call_recorder(
        lambda *args: 'password'
    )
    monkeypatch.setattr(settings.utils, 'get_password',
                        replaced_get_password)
    replaced_get_cacert = pretend.call_recorder(
        lambda *args: 'cacert'
    )
    monkeypatch.setattr(settings.utils, 'get_cacert',
                        replaced_get_cacert)
    replaced_get_clientcert = pretend.call_recorder(
        lambda *args: 'clientcert'
    )
    monkeypatch.setattr(settings.utils, 'get_clientcert',
                        replaced_get_clientcert)
    s = settings.Settings()
    assert (s.repository_config['repository'] ==
            'https://upload.pypi.org/legacy/')
    assert s.sign is False
    assert s.sign_with == 'gpg'
    assert s.identity is None
    assert s.username == 'username'
    assert s.password == 'password'
    assert s.cacert == 'cacert'
    assert s.client_cert == 'clientcert'

    assert replaced_get_clientcert.calls == [
        pretend.call(None, s.repository_config)
    ]
    assert replaced_get_cacert.calls == [
        pretend.call(None, s.repository_config)
    ]
    assert replaced_get_username.calls == [
        pretend.call(None, s.repository_config)
    ]
    assert replaced_get_password.calls == [
        pretend.call(s.repository_config['repository'],
                     'username',
                     None,
                     s.repository_config)
    ]
    assert replaced_normalize_repository_url.calls == [
        pretend.call(s.repository_config['repository'])
    ]
    assert replaced_get_repository_from_config.calls == [
        pretend.call('~/.pypirc', 'pypi', None)
    ]


def test_identity_requires_sign():
    """Verify that if a user passes identity, we require sign=True."""
    with pytest.raises(exceptions.InvalidSigningConfiguration):
        settings.Settings(sign=False, identity='fakeid')
