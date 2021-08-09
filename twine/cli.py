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
from typing import Any, List, Tuple, Dict

from importlib_metadata import entry_points
from importlib_metadata import version

import twine

args = argparse.Namespace()


def list_dependencies_and_versions() -> List[Tuple[str, str]]:
    deps = (
        "importlib_metadata",
        "pkginfo",
        "requests",
        "requests-toolbelt",
        "tqdm",
    )
    return [(dep, version(dep)) for dep in deps]  # type: ignore[no-untyped-call] # python/importlib_metadata#288  # noqa: E501


def dep_versions() -> str:
    return ", ".join(
        "{}: {}".format(*dependency) for dependency in list_dependencies_and_versions()
    )


def dispatch(argv: List[str]) -> Any:
    command_map: Dict[str, Any] = {}
    parser = build_parser(command_map)
    options = parser.parse_args(argv)
    return command_map[options.command].send(options)


def build_parser(command_map: Dict[str, Any] = None):
    if command_map is None:
        command_map = {}
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
    sub_parser = parser.add_subparsers(title='sub command to run', dest='command')
    sub_parser.required = True
    for command in registered_commands:
        main_func = command.load()
        generator = main_func(sub_parser)
        command_map[command.name] = next(generator)
    return parser
