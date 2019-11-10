#!/usr/bin/env python3
import sys

import requests

from twine import exceptions
from twine.cli import dispatch


def main():
    try:
        return dispatch(sys.argv[1:])
    except (exceptions.TwineException, requests.exceptions.HTTPError) as exc:
        return '{}: {}'.format(exc.__class__.__name__, exc.args[0])


if __name__ == "__main__":
    sys.exit(main())
