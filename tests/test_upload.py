# Copyright 2014 Ian Cordasco
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
from __future__ import unicode_literals, print_function

import os
import textwrap

import pytest

from twine.commands import upload

default_kwargs = {
    'dists': None,
    'repository': 'pypi',
    'sign': False,
    'identity': None,
    'username': '',
    'password': '',
    'comment': None,
    'sign_with': 'gpg',
    'config_file': '',
    'verbose_response': False,
}


def test_ensure_wheel_files_uploaded_first():
    files = upload.group_wheel_files_first(["twine/foo.py",
                                            "twine/first.whl",
                                            "twine/bar.py",
                                            "twine/second.whl"])
    expected = ["twine/first.whl",
                "twine/second.whl",
                "twine/foo.py",
                "twine/bar.py"]
    assert expected == files


def test_ensure_if_no_wheel_files():
    files = upload.group_wheel_files_first(["twine/foo.py",
                                            "twine/bar.py"])
    expected = ["twine/foo.py",
                "twine/bar.py"]
    assert expected == files


def test_find_dists_expands_globs():
    files = sorted(upload.find_dists(['twine/__*.py']))
    expected = ['twine/__init__.py', 'twine/__main__.py']
    assert expected == files


def test_find_dists_errors_on_invalid_globs():
    with pytest.raises(ValueError):
        upload.find_dists(['twine/*.rb'])


def test_find_dists_handles_real_files():
    expected = ['twine/__init__.py', 'twine/__main__.py', 'twine/cli.py',
                'twine/utils.py', 'twine/wheel.py']
    files = upload.find_dists(expected)
    assert expected == files


def test_get_config_old_format(tmpdir):
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [server-login]
            username:foo
            password:bar
        """))

    try:
        kwargs = default_kwargs.copy()
        kwargs.update(dict(dists="foo", config_file=pypirc))
        upload.upload(**kwargs)
    except KeyError as err:
        assert err.args[0] == (
            "Missing 'pypi' section from the configuration file.\n"
            "Maybe you have a out-dated '{0}' format?\n"
            "more info: "
            "https://docs.python.org/distutils/packageindex.html#pypirc\n"
        ).format(pypirc)
