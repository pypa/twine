# Copyright 2015 Ian Cordasco
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
from __future__ import absolute_import, unicode_literals, print_function

import argparse
import os.path

from twine import exceptions as exc
from twine.package import PackageFile
from twine.repository import Repository
from twine import utils


def register(package, repository, username, password, comment, config_file,
             cert, client_cert, repository_url):
    config = utils.get_repository_from_config(
        config_file,
        repository,
        repository_url,
    )
    config["repository"] = utils.normalize_repository_url(
        config["repository"]
    )

    print("Registering package to {0}".format(config["repository"]))

    username = utils.get_username(username, config)
    password = utils.get_password(
        config["repository"], username, password, config,
    )
    ca_cert = utils.get_cacert(cert, config)
    client_cert = utils.get_clientcert(client_cert, config)

    repository = Repository(config["repository"], username, password)
    repository.set_certificate_authority(ca_cert)
    repository.set_client_certificate(client_cert)

    if not os.path.exists(package):
        raise exc.PackageNotFound(
            '"{0}" does not exist on the file system.'.format(package)
        )

    resp = repository.register(PackageFile.from_filename(package, comment))
    repository.close()

    if resp.is_redirect:
        raise exc.RedirectDetected(
            ('"{0}" attempted to redirect to "{1}" during registration.'
             ' Aborting...').format(config["repository"],
                                    resp.headers["location"]))

    resp.raise_for_status()


def main(args):
    parser = argparse.ArgumentParser(prog="twine register")
    parser.add_argument(
        "-r", "--repository",
        action=utils.EnvironmentDefault,
        env="TWINE_REPOSITORY",
        default=None,
        help="The repository (package index) to register the package to. "
             "Should be a section in the config file. (Can also be set "
             "via %(env)s environment variable.) "
             "Initial package registration no longer necessary on pypi.org: "
             "https://packaging.python.org/guides/migrating-to-pypi-org/",
    )
    parser.add_argument(
        "--repository-url",
        action=utils.EnvironmentDefault,
        env="TWINE_REPOSITORY_URL",
        default=None,
        required=False,
        help="The repository (package index) URL to register the package to. "
             "This overrides --repository. "
             "(Can also be set via %(env)s environment variable.)"
    )
    parser.add_argument(
        "-u", "--username",
        action=utils.EnvironmentDefault,
        env="TWINE_USERNAME",
        required=False, help="The username to authenticate to the repository "
                             "(package index) as. (Can also be set via "
                             "%(env)s environment variable.)",
    )
    parser.add_argument(
        "-p", "--password",
        action=utils.EnvironmentDefault,
        env="TWINE_PASSWORD",
        required=False, help="The password to authenticate to the repository "
                             "(package index) with. (Can also be set via "
                             "%(env)s environment variable.)",
    )
    parser.add_argument(
        "-c", "--comment",
        help="The comment to include with the distribution file.",
    )
    parser.add_argument(
        "--config-file",
        default="~/.pypirc",
        help="The .pypirc config file to use.",
    )
    parser.add_argument(
        "--cert",
        action=utils.EnvironmentDefault,
        env="TWINE_CERT",
        default=None,
        required=False,
        metavar="path",
        help="Path to alternate CA bundle (can also be set via %(env)s "
             "environment variable).",
    )
    parser.add_argument(
        "--client-cert",
        metavar="path",
        help="Path to SSL client certificate, a single file containing the "
             "private key and the certificate in PEM format.",
    )
    parser.add_argument(
        "package",
        metavar="package",
        help="File from which we read the package metadata.",
    )

    args = parser.parse_args(args)

    # Call the register function with the args from the command line
    register(**vars(args))
