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
import os.path
import textwrap

from twine import exceptions
from twine import settings

import pytest


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


def test_identity_requires_sign():
    """Verify that if a user passes identity, we require sign=True."""
    with pytest.raises(exceptions.InvalidSigningConfiguration):
        settings.Settings(sign=False, identity='fakeid')
