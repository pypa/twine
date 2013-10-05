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

import os.path
import textwrap

from twine.utils import DEFAULT_REPOSITORY, get_config


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

    assert get_config(pypirc) == {
        "pypi": {
            "repository": DEFAULT_REPOSITORY,
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

    assert get_config(pypirc) == {
        "pypi": {
            "repository": DEFAULT_REPOSITORY,
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

    assert get_config(pypirc) == {
        "pypi": {
            "repository": DEFAULT_REPOSITORY,
            "username": "testuser",
            "password": "testpassword",
        },
    }
