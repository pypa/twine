import argparse


def common_arguments(prog):
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument(
        "-r", "--repository",
        default="pypi",
        help="The repository to upload the files to (default: %(default)s)",
    )
    parser.add_argument(
        "-u", "--username",
        help="The username to authenticate to the repository as",
    )
    parser.add_argument(
        "-p", "--password",
        help="The password to authenticate to the repository with",
    )
    return parser
