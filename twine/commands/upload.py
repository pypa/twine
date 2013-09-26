#!/usr/bin/env python
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

import distutils.spawn
import hashlib
import logging
import os.path
import shutil
import tempfile

import pkginfo
import requests

from twine.exceptions import CommandError
from twine.utils import get_distutils_config


logger = logging.getLogger(__name__)


class Upload(object):

    DIST_TYPES = {
        "sdist": pkginfo.SDist,
    }

    DIST_EXTENSIONS = {
        ".tar.gz": "sdist",
    }

    def __call__(self, dists, repository, sign, identity, username, password,
            comment):
        # Check that a nonsensical option wasn't given
        if not sign and identity:
            raise CommandError("--sign must be given along with --identity")

        # Get our config from ~/.pypirc
        config = get_distutils_config(repository)

        session = requests.session()

        for filename in dists:
            # Sign the dist if requested
            if sign:
                gpg_args = ["gpg", "--detach-sign", "-a", filename]
                if identity:
                    gpg_args[2:2] = ["--local-user", identity]
                distutils.spawn.spawn(gpg_args)

            # Extract the metadata from the package
            for ext, dtype in self.DIST_EXTENSIONS.items():
                if filename.endswith(ext):
                    meta = self.DIST_TYPES[dtype](filename)
                    break
            else:
                raise CommandError(
                    "Unknown distribution format: '%s'" %
                    os.path.basename(filename)
                )

            pyversion = None

            # Fill in the data - send all the meta-data in case we need to
            # register a new release
            data = {
                # action
                ":action": "file_upload",
                "protcol_version": "1",

                # identify release
                "name": meta.name,
                "version": meta.version,

                # file content
                "filetype": dtype,
                "pyversion": pyversion,

                # additional meta-data
                "metadata_version": meta.metadata_version,
                "summary": meta.summary,
                "home_page": meta.home_page,
                "author": meta.author,
                "author_email": meta.author_email,
                "maintainer": meta.maintainer,
                "maintainer_email": meta.maintainer_email,
                "license": meta.license,
                "description": meta.description,
                "keywords": meta.keywords,
                "platform": meta.platforms,
                "classifiers": meta.classifiers,
                "download_url": meta.download_url,
                "supported_platform": meta.supported_platforms,
                "comment": comment,

                # PEP 314
                "provides": meta.provides,
                "requires": meta.requires,
                "obsoletes": meta.obsoletes,

                # Metadata 1.2
                "project_urls": meta.project_urls,
                "provides_dist": meta.provides_dist,
                "obsoletes_dist": meta.obsoletes_dist,
                "requires_dist": meta.requires_dist,
                "requires_external": meta.requires_external,
                "requires_python": meta.requires_python,

            }

            with open(filename, "rb") as fp:
                content = fp.read()
                filedata = {
                    "content": (os.path.basename(filename), content),
                }
                data["md5_digest"] = hashlib.md5(content).hexdigest()

            if sign:
                with open(filename + ".asc") as gpg:
                    sigdata = gpg.read()
                    filedata["gpg_signature"] = (
                        os.path.basename(filename) + ".asc",
                        sigdata,
                    )

            resp = session.post(
                config["repository"],
                data=data,
                files=filedata,
                auth=(config.get("username"), config.get("password")),
            )
            resp.raise_for_status()

    def create_parser(self, parser):
        parser.add_argument(
            "-r", "--repository",
            help="The repository to upload the files to",
        )
        parser.add_argument(
            "-s", "--sign",
            action="store_true",
            default=False,
            help="Sign files to upload using gpg",
        )
        parser.add_argument(
            "-i", "--identity",
            help="GPG identity used to sign files",
        )
        parser.add_argument(
            "-u", "--username",
            help="The username to authenticate to the repository as",
        )
        parser.add_argument(
            "-p", "--password",
            help="The password to authenticate to the repository with",
        )
        parser.add_argument(
            "-c", "--comment",
            help="The comment to include with the distribution file",
        )
        parser.add_argument(
            "dists",
            nargs="+",
            metavar="dist",
            help="The distribution files to upload to the repository",
        )
