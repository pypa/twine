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
import twine
from twine.commands.register import register
from twine.commands.upload import upload


def process_arguments(argv):
    parser = argparse.ArgumentParser(prog="twine")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s version {0}".format(twine.__version__),
    )
    subparsers = parser.add_subparsers(title="commands",
                                       help="%(prog)s {command} -h for command specific help")

    # Shared parent parser for common settings
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument(
        "-r", "--repository",
        default="pypi",
        help="The repository to upload the files to (default: %(default)s)",
    )
    shared_parser.add_argument(
        "-u", "--username",
        help="The username to authenticate to the repository as",
    )
    shared_parser.add_argument(
        "-p", "--password",
        help="The password to authenticate to the repository with",
    )

    # Upload parser
    upload_parser = subparsers.add_parser("upload", parents=[shared_parser])
    upload_parser.set_defaults(func=upload)

    upload_parser.add_argument(
        "-s", "--sign",
        action="store_true",
        default=False,
        help="Sign files to upload using gpg",
    )
    upload_parser.add_argument(
        "-i", "--identity",
        help="GPG identity used to sign files",
    )

    upload_parser.add_argument(
        "-c", "--comment",
        help="The comment to include with the distribution file",
    )
    upload_parser.add_argument(
        "dists",
        nargs="+",
        metavar="dist",
        help="The distribution files to upload to the repository, may "
             "additionally contain a .asc file to include an existing "
             "signature with the file upload",
    )

    # Register parser
    register_parser = subparsers.add_parser("register", parents=[shared_parser])
    register_parser.set_defaults(func=register)

    args = parser.parse_args(argv)
    args.func(args)

    # If it makes it here everything is OK
    return 0