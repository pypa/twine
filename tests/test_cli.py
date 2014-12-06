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

import pretend

from twine import cli


def test_dispatch_to_subcommand(monkeypatch):
    process = pretend.stub(
        wait=pretend.call_recorder(lambda: None),
        returncode=0,
    )
    popen = pretend.call_recorder(lambda args: process)
    monkeypatch.setattr(cli.subprocess, "Popen", popen)

    rcode = cli.dispatch(["upload"])

    assert popen.calls == [pretend.call(["twine-upload"])]
    assert process.wait.calls == [pretend.call()]
    assert rcode == process.returncode


def test_catches_enoent():
    try:
        cli.dispatch(["non-existant-command"])
    except SystemExit:
        return
    assert False
