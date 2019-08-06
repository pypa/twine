"""Tests for the Settings class and module."""
# Copyright 2018 Ian Stapleton Cordasco
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
import getpass
import os.path
import textwrap
import pretend
import contextlib

from twine import exceptions
from twine import settings

import pytest


@contextlib.contextmanager
def _stubbing_get_pass(monkeypatch, pwd):
    getpass_recorder = pretend.call_recorder(lambda *a, **kw: pwd)
    with monkeypatch.context() as m:
        m.setattr(getpass, 'getpass', getpass_recorder)
        yield getpass_recorder


def test_settings_takes_no_positional_arguments():
    """Verify that the Settings initialization is kw-only."""
    with pytest.raises(TypeError):
        settings.Settings('a', 'b', 'c')


def test_settings_transforms_config(tmpdir):
    """Verify that the settings object transforms the passed in options."""
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [pypi]
            repository: https://upload.pypi.org/legacy/
            username:username
            password:password
        """))
    s = settings.Settings(config_file=pypirc)
    assert (s.repository_config['repository'] ==
            'https://upload.pypi.org/legacy/')
    assert s.sign is False
    assert s.sign_with == 'gpg'
    assert s.identity is None
    assert s.username == 'username'
    assert s.password == 'password'
    assert s.cacert is None
    assert s.client_cert is None
    assert s.disable_progress_bar is False


def test_identity_requires_sign():
    """Verify that if a user passes identity, we require sign=True."""
    with pytest.raises(exceptions.InvalidSigningConfiguration):
        settings.Settings(sign=False, identity='fakeid')


def test_password_not_required_if_client_cert(monkeypatch):
    """Verify that if client_cert is provided then a password is not."""
    pwd = 'RandomPassword'
    test_client_cert = '/random/path'
    with _stubbing_get_pass(monkeypatch, pwd) as getpass_recorder:
        settings_obj = settings.Settings(
            username='fakeuser', client_cert=test_client_cert)
    assert not settings_obj.password
    assert len(getpass_recorder.calls) == 0
    assert settings_obj.client_cert == test_client_cert


@pytest.mark.parametrize('client_cert', [None, ""])
def test_password_is_required_if_no_client_cert(monkeypatch, client_cert):
    """Verify that if client_cert is not provided then a password must be."""
    pwd = 'RandomPassword'
    with _stubbing_get_pass(monkeypatch, pwd) as getpass_recorder:
        settings_obj = settings.Settings(
            username='fakeuser', client_cert=client_cert)
    assert settings_obj.password == pwd
    assert len(getpass_recorder.calls) > 0


def test_password_and_client_cert_are_set_if_both_given(monkeypatch):
    """Verify that if both password and client_cert are given they are set"""
    pwd = 'RandomPassword'
    client_cert = '/random/path'
    with _stubbing_get_pass(monkeypatch, pwd) as getpass_recorder:
        setting_obj = settings.Settings(
            username='fakeuser', password=pwd, client_cert=client_cert)
    assert setting_obj.password == pwd
    assert setting_obj.client_cert == client_cert
    assert len(getpass_recorder.calls) == 0
