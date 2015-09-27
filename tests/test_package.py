# Copyright 2015 Ian Cordasco
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
from twine import package

import pretend


def test_sign_file(monkeypatch):
    replaced_check_call = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(package.subprocess, 'check_call', replaced_check_call)
    filename = 'tests/fixtures/deprecated-pypirc'

    pkg = package.PackageFile(
        filename=filename,
        comment=None,
        metadata=pretend.stub(name="deprecated-pypirc"),
        python_version=None,
        filetype=None
    )
    try:
        pkg.sign('gpg2', None)
    except IOError:
        pass
    args = ('gpg2', '--detach-sign', '-a', filename)
    assert replaced_check_call.calls == [pretend.call(args)]


def test_sign_file_with_identity(monkeypatch):
    replaced_check_call = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(package.subprocess, 'check_call', replaced_check_call)
    filename = 'tests/fixtures/deprecated-pypirc'

    pkg = package.PackageFile(
        filename=filename,
        comment=None,
        metadata=pretend.stub(name="deprecated-pypirc"),
        python_version=None,
        filetype=None
    )
    try:
        pkg.sign('gpg', 'identity')
    except IOError:
        pass
    args = ('gpg', '--detach-sign', '--local-user', 'identity', '-a', filename)
    assert replaced_check_call.calls == [pretend.call(args)]


def test_package_signed_name_is_correct():
    filename = 'tests/fixtures/deprecated-pypirc'

    pkg = package.PackageFile(
        filename=filename,
        comment=None,
        metadata=pretend.stub(name="deprecated-pypirc"),
        python_version=None,
        filetype=None
    )

    assert pkg.signed_basefilename == "deprecated-pypirc.asc"
    assert pkg.signed_filename == (filename + '.asc')
