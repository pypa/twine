#!/usr/bin/env python3
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
import re
import sys
from typing import Any

import colorama
import requests

from twine import cli
from twine import exceptions


def main() -> Any:
    try:
        return cli.dispatch(sys.argv[1:])
    except requests.HTTPError as exc:
        return _format_error(_format_http_exception(exc))
    except exceptions.TwineException as exc:
        return _format_error(_format_exception(exc))


def _format_http_exception(exc: requests.HTTPError) -> str:
    # '%s Client Error: %s for url: %s'
    # '%s Server Error: %s for url: %s'
    pattern = r"(?P<status>.*Error): (?P<reason>.*) for url: (?P<url>.*)"
    match = re.match(pattern, exc.args[0])
    if match:
        return (
            f"{exc.__class__.__name__} from {match['url']}: {match['status']}\n"
            f"{match['reason']}"
        )
    return _format_exception(exc)


def _format_exception(exc: Exception) -> str:
    return f"{exc.__class__.__name__}: {exc.args[0]}"


def _format_error(message: str) -> str:
    pre_style, post_style = "", ""
    if not cli.args.no_color:
        colorama.init()
        pre_style, post_style = colorama.Fore.RED, colorama.Style.RESET_ALL

    return f"{pre_style}{message}{post_style}"


if __name__ == "__main__":
    sys.exit(main())
