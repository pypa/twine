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

import os.path
import functools
import getpass
import sys

try:
    import configparser
except ImportError:  # pragma: no cover
    import ConfigParser as configparser

# Shim for raw_input in python3
if sys.version_info > (3,):
    input_func = input
else:
    input_func = raw_input


DEFAULT_REPOSITORY = "https://pypi.python.org/pypi"


def get_config(path="~/.pypirc"):
    # Expand user strings in the path
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        return {"pypi": {"repository": DEFAULT_REPOSITORY,
                         "username": None,
                         "password": None
                         }
                }

    # Parse the rc file
    parser = configparser.ConfigParser()
    parser.read(path)

    # Get a list of repositories from the config file
    if (parser.has_section("distutils")
            and parser.has_option("distutils", "index-servers")):
        repositories = parser.get("distutils", "index-servers").split()
    else:
        repositories = ["pypi"]

    config = {}

    defaults = {"username": None, "password": None}
    if parser.has_section("server-login"):
        for key in ["username", "password"]:
            if parser.has_option("server-login", key):
                defaults[key] = parser.get("server-login", key)

    for repository in repositories:
        # Skip this repository if it doesn't exist in the config file
        if not parser.has_section(repository):
            continue

        # Mandatory configuration and defaults
        config[repository] = {
            "repository": DEFAULT_REPOSITORY,
            "username": None,
            "password": None,
        }

        # Optional configuration values
        for key in ["username", "repository", "password"]:
            if parser.has_option(repository, key):
                config[repository][key] = parser.get(repository, key)
            elif defaults.get(key):
                config[repository][key] = defaults[key]

    return config


def get_userpass_value(cli_value, config, key, prompt_strategy):
    """Gets the username / password from config.

    Uses the following rules:

    1. If it is specified on the cli (`cli_value`), use that.
    2. If `config[key]` is specified, use that.
    3. Otherwise prompt using `prompt_strategy`.

    :param cli_value: The value supplied from the command line or `None`.
    :type cli_value: unicode or `None`
    :param config: Config dictionary
    :type config: dict
    :param key: Key to find the config value.
    :type key: unicode
    :prompt_strategy: Argumentless function to return fallback value.
    :type prompt_strategy: function
    :returns: The value for the username / password
    :rtype: unicode
    """
    if cli_value is not None:
        return cli_value
    elif config.get(key):
        return config[key]
    else:
        return prompt_strategy()

get_username = functools.partial(
    get_userpass_value,
    key='username',
    prompt_strategy=functools.partial(input_func, 'Enter your username: '),
)
get_password = functools.partial(
    get_userpass_value,
    key='password',
    prompt_strategy=functools.partial(
        getpass.getpass, 'Enter your password: ',
    ),
)
