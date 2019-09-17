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
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import argparse
import cgi
import re
import sys
from io import StringIO

import readme_renderer.rst

from twine.commands import _find_dists
from twine.package import PackageFile

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


class _WarningStream(object):
    def __init__(self):
        self.output = StringIO()

    def write(self, text):
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

    def __str__(self):
        return self.output.getvalue()


def _check_file(filename, render_warning_stream):
    """Check given distribution."""
    warnings = []
    is_ok = True

    package = PackageFile.from_filename(filename, comment=None)

    metadata = package.metadata_dictionary()
    description = metadata["description"]
    description_content_type = metadata["description_content_type"]

    if description_content_type is None:
        warnings.append(
            '`long_description_content_type` missing.  '
            'defaulting to `text/x-rst`.'
        )
        description_content_type = 'text/x-rst'

    content_type, params = cgi.parse_header(description_content_type)
    renderer = _RENDERERS.get(content_type, _RENDERERS[None])

    if description in {None, 'UNKNOWN\n\n\n'}:
        warnings.append('`long_description` missing.')
    elif renderer:
        rendering_result = renderer.render(
            description, stream=render_warning_stream, **params
        )
        if rendering_result is None:
            is_ok = False

    return warnings, is_ok


# TODO: Replace with textwrap.indent when Python 2 support is dropped
def _indented(text, prefix):
    """Adds 'prefix' to all non-empty lines on 'text'."""
    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if line.strip() else line)
    return ''.join(prefixed_lines())


def check(dists, output_stream=sys.stdout):
    uploads = [i for i in _find_dists(dists) if not i.endswith(".asc")]
    if not uploads:  # Return early, if there are no files to check.
        output_stream.write("No files to check.\n")
        return False

    failure = False

    for filename in uploads:
        output_stream.write("Checking %s: " % filename)
        render_warning_stream = _WarningStream()
        warnings, is_ok = _check_file(filename, render_warning_stream)

        # Print the status and/or error
        if not is_ok:
            failure = True
            output_stream.write("FAILED\n")

            error_text = (
                "`long_description` has syntax errors in markup and "
                "would not be rendered on PyPI.\n"
            )
            output_stream.write(_indented(error_text, "  "))
            output_stream.write(_indented(str(render_warning_stream), "    "))
        elif warnings:
            output_stream.write("PASSED, with warnings\n")
        else:
            output_stream.write("PASSED\n")

        # Print warnings after the status and/or error
        for message in warnings:
            output_stream.write('  warning: ' + message + '\n')

    return failure


def main(args):
    parser = argparse.ArgumentParser(prog="twine check")
    parser.add_argument(
        "dists",
        nargs="+",
        metavar="dist",
        help="The distribution files to check, usually dist/*",
    )

    args = parser.parse_args(args)

    # Call the check function with the arguments from the command line
    return check(args.dists)
