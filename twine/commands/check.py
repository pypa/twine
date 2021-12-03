"""Module containing the logic for ``twine check``."""
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
import argparse
import cgi
import io
import re
import sys
import textwrap
from typing import IO, List, Optional, Tuple, cast

import readme_renderer.rst
from importlib_metadata import entry_points

from twine import commands
from twine import package as package_file

_RENDERERS = {
    None: readme_renderer.rst,  # Default if description_content_type is None
    "text/plain": None,  # Rendering cannot fail
    "text/x-rst": readme_renderer.rst,
    "text/markdown": None,  # Rendering cannot fail
}


# Regular expression used to capture and reformat docutils warnings into
# something that a human can understand. This is loosely borrowed from
# Sphinx: https://github.com/sphinx-doc/sphinx/blob
# /c35eb6fade7a3b4a6de4183d1dd4196f04a5edaf/sphinx/util/docutils.py#L199
_REPORT_RE = re.compile(
    r"^<string>:(?P<line>(?:\d+)?): "
    r"\((?P<level>DEBUG|INFO|WARNING|ERROR|SEVERE)/(\d+)?\) "
    r"(?P<message>.*)",
    re.DOTALL | re.MULTILINE,
)


class _WarningStream:
    def __init__(self) -> None:
        self.output = io.StringIO()

    def write(self, text: str) -> None:
        matched = _REPORT_RE.search(text)

        if not matched:
            self.output.write(text)
            return

        self.output.write(
            "line {line}: {level_text}: {message}\n".format(
                level_text=matched.group("level").capitalize(),
                line=matched.group("line"),
                message=matched.group("message").rstrip("\r\n"),
            )
        )

    def __str__(self) -> str:
        return self.output.getvalue()


def check_long_description(filename: str) -> Tuple[List[str], List[str]]:
    """Check whether the long description can be properly rendered."""
    warnings = []
    errors = []

    package = package_file.PackageFile.from_filename(filename, comment=None)

    metadata = package.metadata_dictionary()
    description = cast(Optional[str], metadata["description"])
    description_content_type = cast(Optional[str], metadata["description_content_type"])

    if description_content_type is None:
        warnings.append(
            "`long_description_content_type` missing. defaulting to `text/x-rst`."
        )
        description_content_type = "text/x-rst"

    content_type, params = cgi.parse_header(description_content_type)
    renderer = _RENDERERS.get(content_type, _RENDERERS[None])

    if description in {None, "UNKNOWN\n\n\n"}:
        warnings.append("`long_description` missing.")
    elif renderer:
        render_warning_stream = _WarningStream()
        rendering_result = renderer.render(
            description, stream=render_warning_stream, **params
        )
        if rendering_result is None:
            error_text = (
                "`long_description` has syntax errors in markup and "
                "would not be rendered on PyPI."
            )
            errors.append(textwrap.indent(error_text, "  "))
            errors.append(textwrap.indent(str(render_warning_stream), "    "))

    return warnings, errors


def check_license(filename: str) -> Tuple[List[str], List[str]]:
    """Check whether a license is properly specified."""
    warnings = []
    errors = []

    package = package_file.PackageFile.from_filename(filename, comment=None)

    metadata = package.metadata_dictionary()
    license = cast(Optional[str], metadata.get("license", None))
    license_classifiers = [
        classifier
        for classifier in metadata.get("classifiers", [])
        if classifier.startswith("License ::")
    ]

    if license is None and not license_classifiers:
        warning = (
            "No license specified. Use one of the `LICENSE ::` classifiers "
            "or the `license` field if no classifier is relevant."
        )
        warnings.append(warning)

    return warnings, errors


def _check_file(filename: str) -> Tuple[List[str], List[str]]:
    """Run all available checkers on FILENAME.

    :param filename:
        Path to the distribution file to analyze
    :return:
        A list of warnings and a list of errors
    """
    warnings = []
    errors = []

    registered_checkers = entry_points(group="twine.registered_checkers")
    for checker in registered_checkers:
        func = checker.load()
        checker_warnings, checker_errors = func(filename)
        warnings.extend(checker_warnings)
        errors.extend(checker_errors)

    return warnings, errors


def check(
    dists: List[str],
    output_stream: IO[str] = sys.stdout,
    strict: bool = False,
) -> bool:
    """Run linters on the distribution files specified as arguments.

    More linters can be added as entry_points (twine.registered_checkers).

    :param dists:
        The distribution files to check.
    :param output_stream:
        The destination of the resulting output.
    :param strict:
        If ``True``, treat warnings as errors.

    :return:
        ``True`` if there are errors, otherwise ``False``.
    """
    uploads = [i for i in commands._find_dists(dists) if not i.endswith(".asc")]
    if not uploads:  # Return early, if there are no files to check.
        output_stream.write("No files to check.\n")
        return False

    failure = False

    for filename in uploads:
        output_stream.write("Checking %s: " % filename)
        warnings, errors = _check_file(filename)

        # Print the status and/or error
        if errors:
            failure = True
            output_stream.write("FAILED\n")
        elif warnings:
            if strict:
                failure = True
                output_stream.write("FAILED, due to warnings\n")
            else:
                output_stream.write("PASSED, with warnings\n")
        else:
            output_stream.write("PASSED\n")

        # Print errors and warnings after the status
        for message in errors:
            output_stream.write("  error: " + message + "\n")
        for message in warnings:
            output_stream.write("  warning: " + message + "\n")

    return failure


def main(args: List[str]) -> bool:
    """Execute the ``check`` command.

    :param args:
        The command-line arguments.

    :return:
        The exit status of the ``check`` command.
    """
    parser = argparse.ArgumentParser(prog="twine check")
    parser.add_argument(
        "dists",
        nargs="+",
        metavar="dist",
        help="The distribution files to check, usually dist/*",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        required=False,
        help="Fail on warnings",
    )

    parsed_args = parser.parse_args(args)

    # Call the check function with the arguments from the command line
    return check(parsed_args.dists, strict=parsed_args.strict)
