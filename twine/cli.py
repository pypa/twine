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

import argparse
import pkg_resources
import setuptools

import requests
import pkginfo

import twine


def _registered_commands(group='twine.registered_commands'):
    return list(pkg_resources.iter_entry_points(group=group))


def dep_versions():
    return 'pkginfo: {0}, requests: {1}, setuptools: {2}'.format(
        pkginfo.Installed(pkginfo).version,
        # __version__ is always defined but requests does not always have
        # PKG-INFO to read from
        requests.__version__,
        setuptools.__version__,
    )


def dispatch(argv):
    registered_commands = _registered_commands()
    parser = argparse.ArgumentParser(prog="twine")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {0} ({1})".format(twine.__version__,
                                                    dep_versions()),
    )
    parser.add_argument(
        "command",
        choices=[c.name for c in registered_commands],
    )
    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(argv)

    command = args.command
    for registered_command in registered_commands:
        if registered_command.name == command:
            break
    else:
        print("{0} is not a valid command.".format(command))
        raise SystemExit(True)

    main = registered_command.load()

    main(args.args)
