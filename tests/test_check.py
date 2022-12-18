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
import textwrap

import build
import pretend
import pytest

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


def build_sdist(src_path, project_files):
    """
    Build a source distribution similar to `python3 -m build --sdist`.

    Returns the absolute path of the built distribution.
    """
    project_files = {
        "pyproject.toml": (
            """
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"
            """
        ),
        **project_files,
    }

    for filename, content in project_files.items():
        (src_path / filename).write_text(textwrap.dedent(content))

    builder = build.ProjectBuilder(src_path)
    return builder.build("sdist", str(src_path / "dist"))


@pytest.mark.parametrize("strict", [False, True])
def test_warns_missing_description(strict, tmp_path, capsys, caplog):
    sdist = build_sdist(
        tmp_path,
        {
            "setup.cfg": (
                """
                [metadata]
                name = test-package
                version = 0.0.1
                """
            ),
        },
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


def test_warns_missing_file(tmp_path, capsys, caplog):
    sdist = build_sdist(
        tmp_path,
        {
            "setup.cfg": (
                """
                [metadata]
                name = test-package
                version = 0.0.1
                long_description = file:README.rst
                long_description_content_type = text/x-rst
                """
            ),
        },
    )

    assert not check.check([sdist])

    assert capsys.readouterr().out == f"Checking {sdist}: PASSED with warnings\n"

    assert caplog.record_tuples == [
        (
            "twine.commands.check",
            logging.WARNING,
            "`long_description` missing.",
        ),
    ]


def test_fails_rst_syntax_error(tmp_path, capsys, caplog):
    sdist = build_sdist(
        tmp_path,
        {
            "setup.cfg": (
                """
                [metadata]
                name = test-package
                version = 0.0.1
                long_description = file:README.rst
                long_description_content_type = text/x-rst
                """
            ),
            "README.rst": (
                """
                ============
                """
            ),
        },
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
    sdist = build_sdist(
        tmp_path,
        {
            "setup.cfg": (
                """
                [metadata]
                name = test-package
                version = 0.0.1
                long_description = file:README.rst
                long_description_content_type = text/x-rst
                """
            ),
            "README.rst": (
                """
                test-package
                ============
                """
            ),
        },
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
    sdist = build_sdist(
        tmp_path,
        {
            "setup.cfg": (
                """
                [metadata]
                name = test-package
                version = 0.0.1
                long_description = file:README.rst
                long_description_content_type = text/x-rst
                """
            ),
            "README.rst": (
                """
                test-package
                ============

                A test package.
                """
            ),
        },
    )

    assert not check.check([sdist])

    assert capsys.readouterr().out == f"Checking {sdist}: PASSED\n"

    assert not caplog.record_tuples


@pytest.mark.parametrize("content_type", ["text/markdown", "text/plain"])
def test_passes_markdown_description(content_type, tmp_path, capsys, caplog):
    sdist = build_sdist(
        tmp_path,
        {
            "setup.cfg": (
                f"""
                [metadata]
                name = test-package
                version = 0.0.1
                long_description = file:README.md
                long_description_content_type = {content_type}
                """
            ),
            "README.md": (
                """
                # test-package

                A test package.
                """
            ),
        },
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


# TODO: Test print() color output

# TODO: Test log formatting
