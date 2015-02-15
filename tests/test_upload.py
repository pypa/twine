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
import pretend
import pytest

from twine.commands import upload


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


def test_sign_file(monkeypatch):
    replaced_check_call = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(upload.subprocess, 'check_call', replaced_check_call)

    upload.sign_file('gpg2', 'my_file.tar.gz', None)
    args = ['gpg2', '--detach-sign', '-a', 'my_file.tar.gz']
    assert replaced_check_call.calls == [pretend.call(args)]


def test_sign_file_with_identity(monkeypatch):
    replaced_check_call = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(upload.subprocess, 'check_call', replaced_check_call)

    upload.sign_file('gpg', 'my_file.tar.gz', 'identity')
    args = ['gpg', '--detach-sign', '--local-user', 'identity', '-a',
            'my_file.tar.gz']
    assert replaced_check_call.calls == [pretend.call(args)]
