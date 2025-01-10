# Copyright 2018 Dustin Ingram
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
import logging

import pretend
import pytest

from tests import helpers
from twine.commands import check


class TestWarningStream:
    def setup_method(self):
        self.stream = check._WarningStream()

    def test_write_match(self):
        self.stream.write("<string>:2: (WARNING/2) Title underline too short.")
        assert self.stream.getvalue() == "line 2: Warning: Title underline too short.\n"

    def test_write_nomatch(self):
        self.stream.write("this does not match")
        assert self.stream.getvalue() == "this does not match"

    def test_str_representation(self):
        self.stream.write("<string>:2: (WARNING/2) Title underline too short.")
        assert str(self.stream) == "line 2: Warning: Title underline too short."


def test_fails_no_distributions(caplog):
    assert not check.check([])
    assert caplog.record_tuples == [
        (
            "twine.commands.check",
            logging.ERROR,
            "No files to check.",
        ),
    ]


def build_sdist_with_metadata(path, metadata):
    name = "test"
    version = "1.2.3"
    sdist = helpers.build_archive(
        path,
        f"{name}-{version}",
        "tar.gz",
        {
            f"{name}-{version}/README": "README",
            f"{name}-{version}/PKG-INFO": metadata,
        },
    )
    return str(sdist)


@pytest.mark.parametrize("strict", [False, True])
def test_warns_missing_description(strict, tmp_path, capsys, caplog):
    sdist = build_sdist_with_metadata(
        tmp_path,
        """\
        Metadata-Version: 2.1
        Name: test
        Version: 1.2.3
        """,
    )

    assert check.check([sdist], strict=strict) is strict

    assert capsys.readouterr().out == f"Checking {sdist}: " + (
        "FAILED due to warnings\n" if strict else "PASSED with warnings\n"
    )

    assert caplog.record_tuples == [
        (
            "twine.commands.check",
            logging.WARNING,
            "`long_description_content_type` missing. defaulting to `text/x-rst`.",
        ),
        (
            "twine.commands.check",
            logging.WARNING,
            "`long_description` missing.",
        ),
    ]


def test_fails_rst_syntax_error(tmp_path, capsys, caplog):
    sdist = build_sdist_with_metadata(
        tmp_path,
        """\
        Metadata-Version: 2.1
        Name: test-package
        Version: 1.2.3
        Description-Content-Type: text/x-rst


        ============

        """,
    )

    assert check.check([sdist])

    assert capsys.readouterr().out == f"Checking {sdist}: FAILED\n"

    assert caplog.record_tuples == [
        (
            "twine.commands.check",
            logging.ERROR,
            "`long_description` has syntax errors in markup "
            "and would not be rendered on PyPI.\n"
            "line 2: Error: Document or section may not begin with a transition.",
        ),
    ]


def test_fails_rst_no_content(tmp_path, capsys, caplog):
    sdist = build_sdist_with_metadata(
        tmp_path,
        """\
        Metadata-Version: 2.1
        Name: test-package
        Version: 1.2.3
        Description-Content-Type: text/x-rst

        test-package
        ============
        """,
    )

    assert check.check([sdist])

    assert capsys.readouterr().out == f"Checking {sdist}: FAILED\n"

    assert caplog.record_tuples == [
        (
            "twine.commands.check",
            logging.ERROR,
            "`long_description` has syntax errors in markup "
            "and would not be rendered on PyPI.\n"
            "No content rendered from RST source.",
        ),
    ]


def test_passes_rst_description(tmp_path, capsys, caplog):
    sdist = build_sdist_with_metadata(
        tmp_path,
        """\
        Metadata-Version: 2.1
        Name: test-package
        Version: 1.2.3
        Description-Content-Type: text/x-rst

        test-package
        ============

        A test package.
        """,
    )

    assert not check.check([sdist])

    assert capsys.readouterr().out == f"Checking {sdist}: PASSED\n"

    assert not caplog.record_tuples


@pytest.mark.parametrize("content_type", ["text/markdown", "text/plain"])
def test_passes_markdown_description(content_type, tmp_path, capsys, caplog):
    sdist = build_sdist_with_metadata(
        tmp_path,
        f"""\
        Metadata-Version: 2.1
        Name: test-package
        Version: 1.2.3
        Description-Content-Type: {content_type}

        # test-package

        A test package.
        """,
    )

    assert not check.check([sdist])

    assert capsys.readouterr().out == f"Checking {sdist}: PASSED\n"

    assert not caplog.record_tuples


def test_main(monkeypatch):
    check_result = pretend.stub()
    check_stub = pretend.call_recorder(lambda a, strict=False: check_result)
    monkeypatch.setattr(check, "check", check_stub)

    assert check.main(["dist/*"]) == check_result
    assert check_stub.calls == [pretend.call(["dist/*"], strict=False)]


def test_check_expands_glob(monkeypatch):
    """Regression test for #1187."""
    warning_stream = pretend.stub()
    warning_stream_cls = pretend.call_recorder(lambda: warning_stream)
    monkeypatch.setattr(check, "_WarningStream", warning_stream_cls)

    check_file = pretend.call_recorder(lambda fn, stream: ([], True))
    monkeypatch.setattr(check, "_check_file", check_file)

    assert not check.main([f"{helpers.FIXTURES_DIR}/*"])

    # check_file is called more than once, indicating the glob has been expanded
    assert len(check_file.calls) > 1


# TODO: Test print() color output

# TODO: Test log formatting
