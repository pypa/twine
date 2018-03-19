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
import argparse
import warnings

try:
    import configparser
except ImportError:  # pragma: no cover
    import ConfigParser as configparser

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

import twine.exceptions

# Shim for raw_input in python3
if sys.version_info > (3,):
    input_func = input
else:
    input_func = raw_input


DEFAULT_REPOSITORY = "https://upload.pypi.org/legacy/"
TEST_REPOSITORY = "https://test.pypi.org/legacy/"


def get_config(path="~/.pypirc"):
    # Expand user strings in the path
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        return {"pypi": {"repository": DEFAULT_REPOSITORY,
                         "username": None,
                         "password": None
                         },
                "pypitest": {"repository": TEST_REPOSITORY,
                             "username": None,
                             "password": None
                             },
                }

    # Parse the rc file
    parser = configparser.RawConfigParser()
    parser.read(path)

    # Get a list of repositories from the config file
    # format: https://docs.python.org/3/distutils/packageindex.html#pypirc
    if (parser.has_section("distutils") and
            parser.has_option("distutils", "index-servers")):
        repositories = parser.get("distutils", "index-servers").split()
    elif parser.has_section("pypi"):
        # Special case: if the .pypirc file has a 'pypi' section,
        # even if there's no list of index servers,
        # be lenient and include that in our list of repositories.
        repositories = ['pypi']
    else:
        repositories = []

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
        for key in [
            "username", "repository", "password",
            "ca_cert", "client_cert",
        ]:
            if parser.has_option(repository, key):
                config[repository][key] = parser.get(repository, key)
            elif defaults.get(key):
                config[repository][key] = defaults[key]

    return config


def get_repository_from_config(config_file, repository, repository_url=None):
    # Get our config from, if provided, command-line values for the
    # repository name and URL, or the .pypirc file
    if repository_url and "://" in repository_url:
        # prefer CLI `repository_url` over `repository` or .pypirc
        return {
            "repository": repository_url,
            "username": None,
            "password": None,
        }
    if repository_url and "://" not in repository_url:
        raise twine.exceptions.UnreachableRepositoryURLDetected(
            "Repository URL {0} has no protocol. Please add "
            "'https://'. \n".format(repository_url))
    try:
        return get_config(config_file)[repository]
    except KeyError:
        msg = (
            "Missing '{repo}' section from the configuration file\n"
            "or not a complete URL in --repository-url.\n"
            "Maybe you have a out-dated '{cfg}' format?\n"
            "more info: "
            "https://docs.python.org/distutils/packageindex.html#pypirc\n"
        ).format(
            repo=repository,
            cfg=config_file
        )
        raise KeyError(msg)


_HOSTNAMES = set(["pypi.python.org", "testpypi.python.org", "upload.pypi.org",
                  "test.pypi.org"])


def normalize_repository_url(url):
    parsed = urlparse(url)
    if parsed.netloc in _HOSTNAMES:
        return urlunparse(("https",) + parsed[1:])
    return urlunparse(parsed)


def check_status_code(response):
    """
    Shouldn't happen, thanks to the UploadToDeprecatedPyPIDetected
    exception, but this is in case that breaks and it does.
    """
    if (response.status_code == 410 and
            response.url.startswith(("https://pypi.python.org",
                                     "https://testpypi.python.org"))):
        print("It appears you're uploading to pypi.python.org (or "
              "testpypi.python.org). You've received a 410 error response. "
              "Uploading to those sites is deprecated. The new sites are "
              "pypi.org and test.pypi.org. Try using "
              "https://upload.pypi.org/legacy/ "
              "(or https://test.pypi.org/legacy/) to upload your packages "
              "instead. These are the default URLs for Twine now. More at "
              "https://packaging.python.org/guides/migrating-to-pypi-org/ ")
    response.raise_for_status()


def get_userpass_value(cli_value, config, key, prompt_strategy=None):
    """Gets the username / password from config.

    Uses the following rules:

    1. If it is specified on the cli (`cli_value`), use that.
    2. If `config[key]` is specified, use that.
    3. If `prompt_strategy`, prompt using `prompt_strategy`.
    4. Otherwise return None

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
    elif prompt_strategy:
        return prompt_strategy()
    else:
        return None


def password_prompt(prompt_text):  # Always expects unicode for our own sanity
    prompt = prompt_text
    # Workaround for https://github.com/pypa/twine/issues/116
    if os.name == 'nt' and sys.version_info < (3, 0):
        prompt = prompt_text.encode('utf8')
    return getpass.getpass(prompt)


def get_password_from_keyring(system, username):
    try:
        import keyring
    except ImportError:
        return

    try:
        return keyring.get_password(system, username)
    except Exception as exc:
        warnings.warn(str(exc))


def password_from_keyring_or_prompt(system, username):
    return (
        get_password_from_keyring(system, username)
        or password_prompt('Enter your password: ')
    )


get_username = functools.partial(
    get_userpass_value,
    key='username',
    prompt_strategy=functools.partial(input_func, 'Enter your username: '),
)
get_cacert = functools.partial(
    get_userpass_value,
    key='ca_cert',
)
get_clientcert = functools.partial(
    get_userpass_value,
    key='client_cert',
)


class EnvironmentDefault(argparse.Action):
    """Get values from environment variable."""

    def __init__(self, env, required=True, default=None, **kwargs):
        default = os.environ.get(env, default)
        self.env = env
        if default:
            required = False
        super(EnvironmentDefault, self).__init__(
            default=default,
            required=required,
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def get_password(system, username, cli_value, config):
    return get_userpass_value(
        cli_value,
        config,
        key='password',
        prompt_strategy=functools.partial(
            password_from_keyring_or_prompt,
            system,
            username,
        ),
    )
