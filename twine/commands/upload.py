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
import os.path
import sys

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

import requests
from requests_toolbelt.multipart import MultipartEncoder

import twine.exceptions as exc
from twine.package import PackageFile
from twine.utils import get_config, get_username, get_password


def group_wheel_files_first(files):
    if not any(fname for fname in files if fname.endswith(".whl")):
        # Return early if there's no wheel files
        return files

    files.sort(key=lambda x: -1 if x.endswith(".whl") else 0)

    return files


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


class Repository(object):
    def __init__(self, repository_url, username, password):
        self.url = repository_url
        self.session = requests.session()
        self.session.auth = (username, password)

    def close(self):
        self.session.close()

    def upload(self, package):
        data = package.metadata_dictionary()
        data.update({
            # action
            ":action": "file_upload",
            "protcol_version": "1",
        })

        data_to_send = []
        for key, value in data.items():
            if isinstance(value, (list, tuple)):
                for item in value:
                    data_to_send.append((key, item))
            else:
                data_to_send.append((key, value))

        print("Uploading {0}".format(package.basefilename))

        with open(package.filename, "rb") as fp:
            data_to_send.append((
                "content",
                (package.basefilename, fp, "application/octet-stream"),
            ))
            encoder = MultipartEncoder(data_to_send)

            resp = self.session.post(
                self.url,
                data=encoder,
                allow_redirects=False,
                headers={'Content-Type': encoder.content_type},
            )

        return resp


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

    repository = Repository(config["repository"], username, password)

    uploads = find_dists(dists)

    for filename in uploads:
        package = PackageFile.from_filename(filename, comment)
        # Sign the dist if requested
        # if sign:
        #     sign_file(sign_with, filename, identity)

        # signed_name = os.path.basename(filename) + ".asc"
        signed_name = package.signed_filename
        if signed_name in signatures:
            with open(signatures[signed_name], "rb") as gpg:
                package.gpg_signature = (signed_name, gpg.read())
                # data["gpg_signature"] = (signed_name, gpg.read())
        elif sign:
            package.sign(sign_with, identity)
            # with open(filename + ".asc", "rb") as gpg:
            #     data["gpg_signature"] = (signed_name, gpg.read())

        resp = repository.upload(package)
        # Bug 28. Try to silence a ResourceWarning by releasing the socket and
        # clearing the connection pool.
        resp.close()

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

    repository.close()


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
