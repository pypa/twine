# Copyright 2013 Donald Stufft
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
import pretend
import pytest

from twine import cli
from twine.commands import upload


def test_dispatch_to_subcommand(monkeypatch):
    replaced_main = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(upload, "main", replaced_main)

    cli.dispatch(["upload", "path/to/file"])

    assert replaced_main.calls == [pretend.call(["path/to/file"])]


def test_catches_enoent():
    with pytest.raises(SystemExit):
        cli.dispatch(["non-existent-command"])
