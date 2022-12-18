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

import pretend
import requests

from twine import __main__ as dunder_main
from twine.commands import upload

# Hard-coding control characters for red text; couldn't find a succinct alternative
RED_ERROR = "\x1b[31mERROR   \x1b[0m"
PLAIN_ERROR = "ERROR   "


def _unwrap_lines(text):
    # Testing wrapped lines was ugly and inconsistent across environments
    return " ".join(line.strip() for line in text.splitlines())


def test_exception_handling(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["twine", "upload", "missing.whl"])

    error = dunder_main.main()
    assert error

    captured = capsys.readouterr()

    assert _unwrap_lines(captured.out) == (
        f"{RED_ERROR} InvalidDistribution: Cannot find file (or expand pattern): "
        "'missing.whl'"
    )


def test_http_exception_handling(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["twine", "upload", "test.whl"])
    monkeypatch.setattr(
        upload,
        "upload",
        pretend.raiser(
            requests.HTTPError(
                response=pretend.stub(
                    url="https://example.org",
                    status_code=400,
                    reason="Error reason",
                )
            )
        ),
    )

    error = dunder_main.main()
    assert error

    captured = capsys.readouterr()

    assert _unwrap_lines(captured.out) == (
        f"{RED_ERROR} HTTPError: 400 Bad Request from https://example.org "
        "Error reason"
    )


def test_no_color_exception(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["twine", "--no-color", "upload", "missing.whl"])

    error = dunder_main.main()
    assert error

    captured = capsys.readouterr()

    assert _unwrap_lines(captured.out) == (
        f"{PLAIN_ERROR} InvalidDistribution: Cannot find file (or expand pattern): "
        "'missing.whl'"
    )


# TODO: Test verbose output formatting
