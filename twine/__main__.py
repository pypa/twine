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
import sys
from typing import Any

import requests

from twine import cli
from twine import exceptions

try:
    import colorama
except Exception:
    colorama = None


def main() -> Any:
    try:
        if colorama:
            colorama.init()
        return cli.dispatch(sys.argv[1:])
    except (exceptions.TwineException, requests.HTTPError) as exc:
        pre_style, post_style = "", ""
        if colorama:
            pre_style, post_style = colorama.Fore.RED, colorama.Style.RESET_ALL

        return "{}{}: {}{}".format(
            pre_style, exc.__class__.__name__, exc.args[0], post_style,
        )


if __name__ == "__main__":
    sys.exit(main())
