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

_VALID_CONTENT_TYPES = sorted([key for key in _RENDERERS.keys() if key])

# Regular expression used to capture and reformat doctuils warnings into
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


def _get_description_content_type(metadata, output_stream):
    description_content_type = metadata["description_content_type"]
    if description_content_type is None:
        output_stream.write(
            'warning: `long_description_content_type` missing.  '
            'defaulting to `text/x-rst`.\n'
        )
        description_content_type = 'text/x-rst'

    if description_content_type not in _VALID_CONTENT_TYPES:
        output_stream.write(
            'warning; `long_description_content_type` invalid.\n'
            'It must be one of the following types: [{}].\n'
            .format(", ".join(_VALID_CONTENT_TYPES))
        )
    return description_content_type


def _get_description(metadata, output_stream):
    description = metadata["description"]
    if description in {None, 'UNKNOWN\n\n\n'}:
        output_stream.write('warning: `long_description` missing.\n')
        return None
    return description


def _description_will_not_render(description_content_type, description):
    warning_stream = _WarningStream()
    content_type, params = cgi.parse_header(description_content_type)
    renderer = _RENDERERS.get(content_type, _RENDERERS[None])
    return (description is not None
            and renderer
            and renderer.render(description, stream=warning_stream, **params)
            is None)


def check_package(package, output_stream):
    warning_stream = _WarningStream()
    metadata = package.metadata_dictionary()
    description_content_type = _get_description_content_type(
        metadata,
        output_stream
    )
    description = _get_description(metadata, output_stream)
    failure = _description_will_not_render(
        description_content_type,
        description
    )
    if failure:
        output_stream.write("Failed\n")
        output_stream.write(
            "The project's long_description has invalid markup which "
            "will not be rendered on PyPI. The following syntax "
            "errors were detected:\n%s" % warning_stream
        )
    else:
        output_stream.write("Passed\n")
    return failure


def check(dists, output_stream=sys.stdout):
    uploads = [i for i in _find_dists(dists) if not i.endswith(".asc")]
    failure = False

    for filename in uploads:
        output_stream.write("Checking distribution %s: " % filename)
        package = PackageFile.from_filename(filename, comment=None)
        failure = check_package(package, output_stream) or failure

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
