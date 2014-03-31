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

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


DEFAULT_REPOSITORY = 'https://pypi.python.org/pypi'


def get_config(path="~/.pypirc"):
    # Expand user strings in the path
    path = os.path.expanduser(path)

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

    return config
