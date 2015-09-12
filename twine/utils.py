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

import os
import os.path
import functools
import getpass
import sys

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

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

    if os.path.isfile(path):
        config = _read_config_file(path)
    else:
        config = _get_default_config()

    env_config = _get_env_config()

    config.update(env_config)
    return config


def _get_default_config():
    return {"pypi": {"repository": DEFAULT_REPOSITORY,
                     "username": None,
                     "password": None
                     }
            }


def _read_config_file(path):
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


def _get_env_config(prefix='pypi_repo_'):
    prefix_norm = prefix.upper()
    prefix_len = len(prefix_norm)

    config = {}

    for key, val in os.environ.items():
        if key.startswith(prefix_norm):
            repo_name = key[prefix_len:].strip().lower().replace('_', '-')
            if not repo_name:
                continue  # wrong repo name, should we log?
            config[repo_name] = _parse_pypi_repo_connection_string(val)

    return config


def _parse_pypi_repo_connection_string(conn_str):
    parsed = urlparse(conn_str)

    # Extract username and password out of netloc
    netloc = parsed.hostname

    if parsed.port:
        netloc += ':%s' % parsed.port

    repository = urlunparse((parsed[0], netloc) + parsed[2:])
    return {
        "repository": repository,
        "username": parsed.username,
        "password": parsed.password,
    }


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
    elif config.get(key) is not None:
        return config[key]
    else:
        return prompt_strategy()


def password_prompt(prompt_text):  # Always expects unicode for our own sanity
    prompt = prompt_text
    # Workaround for https://github.com/pypa/twine/issues/116
    if os.name == 'nt' and sys.version_info < (3, 0):
        prompt = prompt_text.encode('utf8')
    return functools.partial(getpass.getpass, prompt=prompt)

get_username = functools.partial(
    get_userpass_value,
    key='username',
    prompt_strategy=functools.partial(input_func, 'Enter your username: '),
)
get_password = functools.partial(
    get_userpass_value,
    key='password',
    prompt_strategy=password_prompt('Enter your password: '),
)
