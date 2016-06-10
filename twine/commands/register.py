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

import os.path

import click

from twine import exceptions as exc
from twine.cli import twine
from twine.package import PackageFile
from twine.repository import Repository
from twine import utils


def register(package, repository, username, password, comment, config_file,
             cert, client_cert):
    config = utils.get_repository_from_config(config_file, repository)
    config["repository"] = utils.normalize_repository_url(
        config["repository"]
    )

    print("Registering package to {0}".format(config["repository"]))

    username = utils.get_username(username, config)
    password = utils.get_password(password, config)
    ca_cert = utils.get_cacert(cert, config)
    client_cert = utils.get_clientcert(client_cert, config)

    repository = Repository(config["repository"], username, password)
    repository.set_certificate_authority(ca_cert)
    repository.set_client_certificate(client_cert)

    resp = repository.register(PackageFile.from_filename(package, comment))
    repository.close()

    if resp.is_redirect:
        raise exc.RedirectDetected(
            ('"{0}" attempted to redirect to "{1}" during registration.'
             ' Aborting...').format(config["repository"],
                                    resp.headers["location"]))

    resp.raise_for_status()


@twine.command(name="register")
@click.option(
    "-r", "--repository",
    default="pypi",
    help="The repository to upload the files to.",
)
@click.option(
    "-u", "--username",
    help="The username to authenticate to the repository as",
)
@click.option(
    "-p", "--password",
    help="The password to authenticate to the repository with",
)
@click.option(
    "-c", "--comment",
    help="The comment to include with the distribution file",
)
@click.option(
    "--config-file",
    default=os.path.expanduser("~/.pypirc"),
    help="The .pypirc config file to use",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
)
@click.option(
    "--cert",
    help="Path to alternate CA bundle",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
)
@click.option(
    "--client-cert",
    help=("Path to SSL client certificate, a single file containing the "
          "private key and the certificate in PEM forma"),
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
)
@click.argument(
    "package",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
)
def main(*args, **kwargs):
    return register(*args, **kwargs)
