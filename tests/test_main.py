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

import sys

import pytest

from twine import __main__ as dunder_main


def test_exception_handling(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["twine", "upload", "missing.whl"])

    error = dunder_main.main()
    assert error

    captured = capsys.readouterr()

    # Removing trailing whitespace on lines wrapped by Rich; trying to test it was ugly.
    # TODO: Assert color
    assert [line.rstrip() for line in captured.out.splitlines()] == [
        "ERROR    InvalidDistribution: Cannot find file (or expand pattern):",
        "         'missing.whl'",
    ]


@pytest.mark.xfail(reason="capsys isn't reset, resulting in duplicate lines")
def test_no_color_exception(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["twine", "--no-color", "upload", "missing.whl"])

    error = dunder_main.main()
    assert error

    captured = capsys.readouterr()

    # Removing trailing whitespace on lines wrapped by Rich; trying to test it was ugly.
    # TODO: Assert no color
    assert [line.rstrip() for line in captured.out.splitlines()] == [
        "ERROR    InvalidDistribution: Cannot find file (or expand pattern):",
        "         'missing.whl'",
    ]


# TODO: Test verbose output formatting
