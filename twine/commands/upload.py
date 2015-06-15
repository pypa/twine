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

import argparse
import glob
import hashlib
import itertools
import os.path
import subprocess
import sys

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

import pkginfo
import pkg_resources
import requests
from requests_toolbelt.multipart import MultipartEncoder

import twine.exceptions as exc
from twine.utils import get_config, get_username, get_password
from twine.wheel import Wheel
from twine.wininst import WinInst


DIST_TYPES = {
    "bdist_wheel": Wheel,
    "bdist_wininst": WinInst,
    "bdist_egg": pkginfo.BDist,
    "sdist": pkginfo.SDist,
}

DIST_EXTENSIONS = {
    ".whl": "bdist_wheel",
    ".exe": "bdist_wininst",
    ".egg": "bdist_egg",
    ".tar.bz2": "sdist",
    ".tar.gz": "sdist",
    ".zip": "sdist",
}


def group_wheel_files_first(dist_files):
    if not any(fname for fname in dist_files if fname.endswith(".whl")):
        # Return early if there's no wheel files
        return dist_files

    group_func = lambda x: x.endswith(".whl")
    sorted_distfiles = sorted(dist_files, key=group_func)
    wheels, not_wheels = [], []
    for grp, files in itertools.groupby(sorted_distfiles, key=group_func):
        if grp:
            wheels.extend(files)
        else:
            not_wheels.extend(files)

    return wheels + not_wheels


def find_dists(dists):
    uploads = []
    for filename in dists:
        if os.path.exists(filename):
            uploads.append(filename)
            continue
        # The filename didn't exist so it may be a glob
        files = glob.glob(filename)
        # If nothing matches, files is []
        if not files:
            raise ValueError(
                "Cannot find file (or expand pattern): '%s'" % filename
                )
        # Otherwise, files will be filenames that exist
        uploads.extend(files)
    return group_wheel_files_first(uploads)


def sign_file(sign_with, filename, identity):
    print("Signing {0}".format(os.path.basename(filename)))
    gpg_args = [sign_with, "--detach-sign", "-a", filename]
    if identity:
        gpg_args[2:2] = ["--local-user", identity]
    subprocess.check_call(gpg_args)


def upload(dists, repository, sign, identity, username, password, comment,
           sign_with, config_file):
    # Check that a nonsensical option wasn't given
    if not sign and identity:
        raise ValueError("sign must be given along with identity")

    # Determine if the user has passed in pre-signed distributions
    signatures = dict(
        (os.path.basename(d), d) for d in dists if d.endswith(".asc")
    )
    dists = [i for i in dists if not i.endswith(".asc")]

    # Get our config from the .pypirc file
    try:
        config = get_config(config_file)[repository]
    except KeyError:
        msg = (
            "Missing '{repo}' section from the configuration file.\n"
            "Maybe you have a out-dated '{cfg}' format?\n"
            "more info: "
            "https://docs.python.org/distutils/packageindex.html#pypirc\n"
        ).format(
            repo=repository,
            cfg=config_file
        )
        raise KeyError(msg)

    parsed = urlparse(config["repository"])
    if parsed.netloc in ["pypi.python.org", "testpypi.python.org"]:
        config["repository"] = urlunparse(
            ("https",) + parsed[1:]
        )

    print("Uploading distributions to {0}".format(config["repository"]))

    username = get_username(username, config)
    password = get_password(password, config)

    session = requests.session()

    uploads = find_dists(dists)

    for filename in uploads:
        # Sign the dist if requested
        if sign:
            sign_file(sign_with, filename, identity)

        # Extract the metadata from the package
        for ext, dtype in DIST_EXTENSIONS.items():
            if filename.endswith(ext):
                meta = DIST_TYPES[dtype](filename)
                break
        else:
            raise ValueError(
                "Unknown distribution format: '%s'" %
                os.path.basename(filename)
            )

        if dtype == "bdist_egg":
            pkgd = pkg_resources.Distribution.from_filename(filename)
            py_version = pkgd.py_version
        elif dtype == "bdist_wheel":
            py_version = meta.py_version
        elif dtype == "bdist_wininst":
            py_version = meta.py_version
        else:
            py_version = None

        # Fill in the data - send all the meta-data in case we need to
        # register a new release
        data = {
            # action
            ":action": "file_upload",
            "protcol_version": "1",

            # identify release
            "name": pkg_resources.safe_name(meta.name),
            "version": meta.version,

            # file content
            "filetype": dtype,
            "pyversion": py_version,

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

        md5_hash = hashlib.md5()
        with open(filename, "rb") as fp:
            content = fp.read(4096)
            while content:
                md5_hash.update(content)
                content = fp.read(4096)

        data["md5_digest"] = md5_hash.hexdigest()

        signed_name = os.path.basename(filename) + ".asc"
        if signed_name in signatures:
            with open(signatures[signed_name], "rb") as gpg:
                data["gpg_signature"] = (signed_name, gpg.read())
        elif sign:
            with open(filename + ".asc", "rb") as gpg:
                data["gpg_signature"] = (signed_name, gpg.read())

        print("Uploading {0}".format(os.path.basename(filename)))

        data_to_send = []
        for key, value in data.items():
            if isinstance(value, (list, tuple)):
                for item in value:
                    data_to_send.append((key, item))
            else:
                data_to_send.append((key, value))

        with open(filename, "rb") as fp:
            data_to_send.append((
                "content",
                (os.path.basename(filename), fp, "application/octet-stream"),
            ))
            encoder = MultipartEncoder(data_to_send)
            resp = session.post(
                config["repository"],
                data=encoder,
                auth=(username, password),
                allow_redirects=False,
                headers={'Content-Type': encoder.content_type},
            )
        # Bug 28. Try to silence a ResourceWarning by releasing the socket and
        # clearing the connection pool.
        resp.close()
        session.close()

        # Bug 92. If we get a redirect we should abort because something seems
        # funky. The behaviour is not well defined and redirects being issued
        # by PyPI should never happen in reality. This should catch malicious
        # redirects as well.
        if resp.is_redirect:
            raise exc.RedirectDetected(
                ('"{0}" attempted to redirect to "{1}" during upload.'
                 ' Aborting...').format(config["respository"],
                                        resp.headers["location"]))
        # Otherwise, raise an HTTPError based on the status code.
        resp.raise_for_status()


def main(args):
    parser = argparse.ArgumentParser(prog="twine upload")
    parser.add_argument(
        "-r", "--repository",
        default="pypi",
        help="The repository to upload the files to (default: %(default)s)",
    )
    parser.add_argument(
        "-s", "--sign",
        action="store_true",
        default=False,
        help="Sign files to upload using gpg",
    )
    parser.add_argument(
        "--sign-with",
        default="gpg",
        help="GPG program used to sign uploads (default: %(default)s)",
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
        "--config-file",
        default="~/.pypirc",
        help="The .pypirc config file to use",
    )
    parser.add_argument(
        "dists",
        nargs="+",
        metavar="dist",
        help="The distribution files to upload to the repository, may "
             "additionally contain a .asc file to include an existing "
             "signature with the file upload",
    )

    args = parser.parse_args(args)

    # Call the upload function with the arguments from the command line
    try:
        upload(**vars(args))
    except Exception as exc:
        sys.exit("{exc.__class__.__name__}: {exc}".format(exc=exc))


if __name__ == "__main__":
    sys.exit(main())
