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

import setuptools

import click
import requests
import pkginfo

from twine import __version__
from twine._installed import Installed


def dep_versions():
    return 'pkginfo: {0}, requests: {1}, setuptools: {2}'.format(
        Installed(pkginfo).version,
        # __version__ is always defined but requests does not always have
        # PKG-INFO to read from
        requests.__version__,
        setuptools.__version__,
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    message="%(prog)s version {0} ({1})".format(__version__, dep_versions()),
)
def twine():
    pass
