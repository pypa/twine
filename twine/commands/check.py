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
import email.message
import io
import logging
import re
from typing import Dict, List, Optional, Tuple, cast

import readme_renderer.rst
from rich import print
from trove_classifiers import classifiers as all_classifiers

from twine import commands
from twine import package as package_file

logger = logging.getLogger(__name__)


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


class _WarningStream(io.StringIO):
    def write(self, text: str) -> int:
        matched = _REPORT_RE.search(text)
        if matched:
            line = matched.group("line")
            level_text = matched.group("level").capitalize()
            message = matched.group("message").rstrip("\r\n")
            text = f"line {line}: {level_text}: {message}\n"

        return super().write(text)

    def __str__(self) -> str:
        return self.getvalue().strip()


def _parse_content_type(value: str) -> Tuple[str, Dict[str, str]]:
    """Implement logic of deprecated cgi.parse_header().

    From https://docs.python.org/3.11/library/cgi.html#cgi.parse_header.
    """
    msg = email.message.EmailMessage()
    msg["content-type"] = value
    return msg.get_content_type(), msg["content-type"].params


def _check_file(
    filename: str, render_warning_stream: _WarningStream
) -> Tuple[List[str], List[str]]:
    """Check given distribution."""
    warnings = []
    errors = []

    package = package_file.PackageFile.from_filename(filename, comment=None)
    metadata = package.metadata_dictionary()

    # Check description
    description = cast(Optional[str], metadata["description"])
    description_content_type = cast(Optional[str], metadata["description_content_type"])

    if description_content_type is None:
        warnings.append(
            "`long_description_content_type` missing. defaulting to `text/x-rst`."
        )
        description_content_type = "text/x-rst"

    content_type, params = _parse_content_type(description_content_type)
    renderer = _RENDERERS.get(content_type, _RENDERERS[None])

    if description is None or description.rstrip() == "UNKNOWN":
        warnings.append("`long_description` missing.")
    elif renderer:
        rendering_result = renderer.render(
            description, stream=render_warning_stream, **params
        )
        if rendering_result is None:
            errors.append(
                "`long_description` has syntax errors in markup"
                " and would not be rendered on PyPI."
            )

    # Check classifiers
    dist_classifiers = cast(Optional[List[str]], metadata["classifiers"])
    for classifier in dist_classifiers:
        if classifier not in all_classifiers:
            errors.append(
                f"`{classifier}` is not a valid classifier"
                f" and would prevent upload to PyPI."
            )

    return warnings, errors


def check(
    dists: List[str],
    strict: bool = False,
) -> bool:
    """Check that a distribution will upload and render correctly on PyPI.

    This currently validates
    - ``long_description``, to make sure it would render correctly on PyPI
    - ``classifiers``, to make sure that all classifiers are valid

    :param dists:
        The distribution files to check.
    :param strict:
        If ``True``, treat warnings as errors.

    :return:
        ``True`` if there are rendering errors, otherwise ``False``.
    """
    uploads = [i for i in commands._find_dists(dists) if not i.endswith(".asc")]
    if not uploads:  # Return early, if there are no files to check.
        logger.error("No files to check.")
        return False

    failure = False

    for filename in uploads:
        print(f"Checking {filename}: ", end="")
        render_warning_stream = _WarningStream()
        warnings, errors = _check_file(filename, render_warning_stream)

        # Print the status and/or error
        if errors:
            failure = True
            print("[red]FAILED[/red]")
            error_mgs = "\n".join(errors)
            logger.error(f"{error_mgs}\n" f"{render_warning_stream}")
        elif warnings:
            if strict:
                failure = True
                print("[red]FAILED due to warnings[/red]")
            else:
                print("[yellow]PASSED with warnings[/yellow]")
        else:
            print("[green]PASSED[/green]")

        # Print warnings after the status and/or error
        for message in warnings:
            logger.warning(message)

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
