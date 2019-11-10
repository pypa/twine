import argparse
import pkg_resources
import setuptools

import tqdm
import requests
import requests_toolbelt
import pkginfo

import twine
from twine._installed import Installed


def _registered_commands(group='twine.registered_commands'):
    registered_commands = pkg_resources.iter_entry_points(group=group)
    return {c.name: c for c in registered_commands}


def list_dependencies_and_versions():
    return [
        ('pkginfo', Installed(pkginfo).version),
        ('requests', requests.__version__),
        ('setuptools', setuptools.__version__),
        ('requests-toolbelt', requests_toolbelt.__version__),
        ('tqdm', tqdm.__version__),
    ]


def dep_versions():
    return ', '.join(
        '{}: {}'.format(*dependency)
        for dependency in list_dependencies_and_versions()
    )


def dispatch(argv):
    registered_commands = _registered_commands()
    parser = argparse.ArgumentParser(prog="twine")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {} ({})".format(
            twine.__version__,
            dep_versions(),
        ),
    )
    parser.add_argument(
        "command",
        choices=registered_commands.keys(),
    )
    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(argv)

    main = registered_commands[args.command].load()

    return main(args.args)
