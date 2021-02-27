# Copyright 2013 Donald Stufft
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
from typing import Any, List, Tuple

import pkginfo
import requests
import requests_toolbelt
import tqdm
from importlib_metadata import entry_points

import twine
from twine import _installed

args = argparse.Namespace()


def list_dependencies_and_versions() -> List[Tuple[str, str]]:
    return [
        ("pkginfo", _installed.Installed(pkginfo).version),
        ("requests", requests.__version__),
        ("requests-toolbelt", requests_toolbelt.__version__),
        ("tqdm", tqdm.__version__),
    ]


def dep_versions() -> str:
    return ", ".join(
        "{}: {}".format(*dependency) for dependency in list_dependencies_and_versions()
    )


def dispatch(argv: List[str]) -> Any:
    registered_commands = entry_points(group="twine.registered_commands")
    parser = argparse.ArgumentParser(prog="twine")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {} ({})".format(twine.__version__, dep_versions()),
    )
    parser.add_argument(
        "--no-color",
        default=False,
        required=False,
        action="store_true",
        help="disable colored output",
    )
    parser.add_argument(
        "command",
        choices=registered_commands.names,
    )
    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    parser.parse_args(argv, namespace=args)

    main = registered_commands[args.command].load()

    return main(args.args)
