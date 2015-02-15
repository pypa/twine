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

import os
import itertools

import pretend
import pytest

from twine.commands import upload


class TestLocalStream:
    def test_find_dists_expands_globs(self):
        dists = upload.LocalStream.find('twine/__*.py')
        files = sorted(dist.name for dist in dists)
        expected = ['twine/__init__.py', 'twine/__main__.py']
        expected = list(map(os.path.normpath, expected))
        assert expected == files

    def test_find_dists_errors_on_invalid_globs(self):
        with pytest.raises(ValueError):
            upload.LocalStream.find('twine/*.rb')


    def test_find_dists_handles_real_files(self):
        expected = ['twine/__init__.py', 'twine/__main__.py', 'twine/cli.py',
                    'twine/utils.py', 'twine/wheel.py']
        finds = map(upload.LocalStream.find, expected)
        results = list(itertools.chain.from_iterable(finds))
        assert all(
            isinstance(result, upload.LocalStream)
            for result in results
        )
        names = [res.name for res in results]
        assert expected == names

    def test_sign_file(self, monkeypatch):
        replaced_check_call = pretend.call_recorder(lambda args: None)
        monkeypatch.setattr(upload.subprocess, 'check_call', replaced_check_call)

        ls = upload.LocalStream('my_file.tar.gz')
        ls.sign(identity=None, sign_with='gpg2')
        args = ['gpg2', '--detach-sign', '-a', 'my_file.tar.gz']
        assert replaced_check_call.calls == [pretend.call(args)]

    def test_sign_file_with_identity(self, monkeypatch):
        replaced_check_call = pretend.call_recorder(lambda args: None)
        monkeypatch.setattr(upload.subprocess, 'check_call', replaced_check_call)

        ls = upload.LocalStream('my_file.tar.gz')
        ls.sign(identity='identity', sign_with='gpg')
        args = ['gpg', '--detach-sign', '--local-user', 'identity', '-a',
                'my_file.tar.gz']
        assert replaced_check_call.calls == [pretend.call(args)]
