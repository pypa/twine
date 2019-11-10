import argparse
import os.path

from twine.package import PackageFile
from twine import exceptions
from twine import settings


def register(register_settings, package):
    repository_url = register_settings.repository_config['repository']

    print(f"Registering package to {repository_url}")
    repository = register_settings.create_repository()

    if not os.path.exists(package):
        raise exceptions.PackageNotFound(
            f'"{package}" does not exist on the file system.'
        )

    resp = repository.register(
        PackageFile.from_filename(package, register_settings.comment)
    )
    repository.close()

    if resp.is_redirect:
        raise exceptions.RedirectDetected.from_args(
            repository_url,
            resp.headers["location"],
        )

    resp.raise_for_status()


def main(args):
    parser = argparse.ArgumentParser(
        prog="twine register",
        description="register operation is not required with PyPI.org",
    )
    settings.Settings.register_argparse_arguments(parser)
    parser.add_argument(
        "package",
        metavar="package",
        help="File from which we read the package metadata.",
    )

    args = parser.parse_args(args)
    register_settings = settings.Settings.from_argparse(args)

    # Call the register function with the args from the command line
    register(register_settings, args.package)
