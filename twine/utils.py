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
from typing import Callable, DefaultDict, Dict, Optional

import os
import os.path
import functools
import getpass
import argparse
import warnings
import collections
import configparser
from urllib.parse import urlparse, urlunparse

import requests
import keyring

from twine import exceptions

# Shim for input to allow testing.
input_func = input

DEFAULT_REPOSITORY = "https://upload.pypi.org/legacy/"
TEST_REPOSITORY = "https://test.pypi.org/legacy/"

# TODO: In general, it seems to be assumed that the values retrieved from
# instances of this type aren't None, except for username and password.
# Type annotations would be cleaner if this were Dict[str, str], but that
# requires reworking the username/password handling, probably starting with
# get_userpass_value.
RepositoryConfig = Dict[str, Optional[str]]


def get_config(path: str = "~/.pypirc") -> Dict[str, RepositoryConfig]:
    # even if the config file does not exist, set up the parser
    # variable to reduce the number of if/else statements
    parser = configparser.RawConfigParser()

    # this list will only be used if index-servers
    # is not defined in the config file
    index_servers = ["pypi", "testpypi"]

    # default configuration for each repository
    defaults: RepositoryConfig = {"username": None, "password": None}

    # Expand user strings in the path
    path = os.path.expanduser(path)

    # Parse the rc file
    if os.path.isfile(path):
        parser.read(path)

        # Get a list of index_servers from the config file
        # format: https://docs.python.org/3/distutils/packageindex.html#pypirc
        if parser.has_option("distutils", "index-servers"):
            index_servers = parser.get("distutils", "index-servers").split()

        for key in ["username", "password"]:
            if parser.has_option("server-login", key):
                defaults[key] = parser.get("server-login", key)

    config: DefaultDict[str, RepositoryConfig] = \
        collections.defaultdict(lambda: defaults.copy())

    # don't require users to manually configure URLs for these repositories
    config["pypi"]["repository"] = DEFAULT_REPOSITORY
    if "testpypi" in index_servers:
        config["testpypi"]["repository"] = TEST_REPOSITORY

    # optional configuration values for individual repositories
    for repository in index_servers:
        for key in [
            "username", "repository", "password",
            "ca_cert", "client_cert",
        ]:
            if parser.has_option(repository, key):
                config[repository][key] = parser.get(repository, key)

    # convert the defaultdict to a regular dict at this point
    # to prevent surprising behavior later on
    return dict(config)


def get_repository_from_config(
    config_file: str,
    repository: str,
    repository_url: Optional[str] = None
) -> RepositoryConfig:
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
        raise exceptions.UnreachableRepositoryURLDetected(
            "Repository URL {} has no protocol. Please add "
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
        raise exceptions.InvalidConfiguration(msg)


_HOSTNAMES = {"pypi.python.org", "testpypi.python.org", "upload.pypi.org",
              "test.pypi.org"}


def normalize_repository_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc in _HOSTNAMES:
        return urlunparse(("https",) + parsed[1:])
    return urlunparse(parsed)


def check_status_code(response: requests.Response, verbose: bool) -> None:
    """Generate a helpful message based on the response from the repository.

    Raise a custom exception for recognized errors. Otherwise, print the
    response content (based on the verbose option) before re-raising the
    HTTPError.
    """
    if response.status_code == 410 and "pypi.python.org" in response.url:
        raise exceptions.UploadToDeprecatedPyPIDetected(
            f"It appears you're uploading to pypi.python.org (or "
            f"testpypi.python.org). You've received a 410 error response. "
            f"Uploading to those sites is deprecated. The new sites are "
            f"pypi.org and test.pypi.org. Try using {DEFAULT_REPOSITORY} (or "
            f"{TEST_REPOSITORY}) to upload your packages instead. These are "
            f"the default URLs for Twine now. More at "
            f"https://packaging.python.org/guides/migrating-to-pypi-org/.")
    elif response.status_code == 405 and "pypi.org" in response.url:
        raise exceptions.InvalidPyPIUploadURL(
            f"It appears you're trying to upload to pypi.org but have an "
            f"invalid URL. You probably want one of these two URLs: "
            f"{DEFAULT_REPOSITORY} or {TEST_REPOSITORY}. Check your "
            f"--repository-url value.")

    try:
        response.raise_for_status()
    except requests.HTTPError as err:
        if response.text:
            if verbose:
                print('Content received from server:\n{}'.format(
                    response.text))
            else:
                print('NOTE: Try --verbose to see response content.')
        raise err


def get_userpass_value(
    cli_value: Optional[str],
    config: RepositoryConfig,
    key: str,
    prompt_strategy: Optional[Callable] = None
) -> Optional[str]:
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
    elif config.get(key) is not None:
        return config[key]
    elif prompt_strategy:
        return prompt_strategy()
    else:
        return None


# TODO: Compare this to get_password_from_keyring
# They seem to do similar things, but this has more exception handling
# Could they have a similar (maybe simpler) structure?
def get_username_from_keyring(system: str) -> Optional[str]:
    try:
        creds = keyring.get_credential(system, None)
        if creds:
            return creds.username
    except AttributeError:
        # To support keyring prior to 15.2
        pass
    except Exception as exc:
        warnings.warn(str(exc))

    return None


def password_prompt(prompt_text: str) -> str:
    return getpass.getpass(prompt_text)


def get_password_from_keyring(system: str, username: str) -> Optional[str]:
    try:
        return keyring.get_password(system, username)
    except Exception as exc:
        warnings.warn(str(exc))

    return None


def username_from_keyring_or_prompt(system: str, prompt_func: Callable) -> str:
    return (
        get_username_from_keyring(system)
        or prompt_func()
    )


def password_from_keyring_or_prompt(
    system: str,
    username: str,
    prompt_func: Callable
) -> str:
    return (
        get_password_from_keyring(system, username)
        or prompt_func()
    )


def raises_noninteractive_exc(message: str) -> None:
    raise exceptions.NonInteractive(message)


def generate_prompt_func_from(
    prompt_func: Callable,
    prompt_type: str,
    non_interactive: bool = False
) -> Callable:
    if non_interactive:
        error_message = "Credential not found for {}.".format(prompt_type)
        return functools.partial(
            raises_noninteractive_exc,
            error_message,
        )
    else:
        message = "Enter your {}: ".format(prompt_type)
        return functools.partial(
            prompt_func,
            message,
        )


def get_username(
    system: str,
    cli_value: Optional[str],
    config: RepositoryConfig,
    non_interactive: bool = False
) -> Optional[str]:
    prompt_func = generate_prompt_func_from(
        input_func,
        'username',
        non_interactive,
    )
    return get_userpass_value(
        cli_value,
        config,
        key='username',
        prompt_strategy=functools.partial(
            username_from_keyring_or_prompt,
            system,
            prompt_func,
        )
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

    def __init__(
        self,
        env: str,
        required: bool = True,
        default: Optional[str] = None,
        **kwargs
    ) -> None:
        default = os.environ.get(env, default)
        self.env = env
        if default:
            required = False
        super().__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def get_password(
    system: str,
    username: Optional[str],
    cli_value: Optional[str],
    config: RepositoryConfig,
    non_interactive: bool = False
) -> Optional[str]:
    prompt_func = generate_prompt_func_from(
        password_prompt,
        'password',
        non_interactive,
    )
    return get_userpass_value(
        cli_value,
        config,
        key='password',
        prompt_strategy=functools.partial(
            password_from_keyring_or_prompt,
            system,
            username,
            prompt_func,
        ),
    )
