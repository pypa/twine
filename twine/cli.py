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
import logging
from typing import Any, List, Tuple

import importlib_metadata
import rich.console
import rich.highlighter
import rich.logging
import rich.theme
from packaging import requirements

import twine

args = argparse.Namespace()

# This module attribute facilitates project-wide configuration and usage of Rich.
# https://rich.readthedocs.io/en/latest/console.html
console = rich.console.Console(
    # Setting force_terminal makes testing easier by ensuring color codes.
    # This could be based on FORCE_COLORS or PY_COLORS in os.environ, but Rich doesn't
    # support that (https://github.com/Textualize/rich/issues/343), and since this is
    # a module attribute, os.environ would be read on import, which complicates testing.
    # no_color is set in dispatch() after argparse.
    force_terminal=True,
    theme=rich.theme.Theme(
        {
            "logging.level.debug": "green",
            "logging.level.info": "blue",
            "logging.level.warning": "yellow",
            "logging.level.error": "red",
            "logging.level.critical": "reverse red",
        }
    ),
)


def configure_logging() -> None:
    root_logger = logging.getLogger("twine")

    # This prevents failures test_main.py due to capsys not being cleared.
    # TODO: Use dictConfig() instead?
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    root_logger.addHandler(
        rich.logging.RichHandler(
            console=console,
            show_time=False,
            show_path=False,
            highlighter=rich.highlighter.NullHighlighter(),
        )
    )


def list_dependencies_and_versions() -> List[Tuple[str, str]]:
    requires = importlib_metadata.requires("twine")  # type: ignore[no-untyped-call] # python/importlib_metadata#288  # noqa: E501
    deps = [requirements.Requirement(r).name for r in requires]
    return [(dep, importlib_metadata.version(dep)) for dep in deps]  # type: ignore[no-untyped-call] # python/importlib_metadata#288  # noqa: E501


def dep_versions() -> str:
    return ", ".join(
        "{}: {}".format(*dependency) for dependency in list_dependencies_and_versions()
    )


def dispatch(argv: List[str]) -> Any:
    registered_commands = importlib_metadata.entry_points(
        group="twine.registered_commands"
    )

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

    # HACK: This attribute isn't documented, but this is an expedient way to alter the
    # Rich configuration after argparse, while allowing logging to be configured on
    # startup, ensuring all errors are displayed.
    console.no_color = args.no_color

    main = registered_commands[args.command].load()

    return main(args.args)
