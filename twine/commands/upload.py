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
import os.path
import subprocess
import sys
import io
import contextlib
import tempfile
import itertools

try:
    from urlparse import urlparse, urlunparse
    from urllib2 import urlopen
except ImportError:
    from urllib.parse import urlparse, urlunparse
    from urllib.request import urlopen

import pkginfo
import pkg_resources
import requests

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


class LocalStream(object):
    """
    A file stream, in a local file
    """
    def __init__(self, name):
        self.name = name

    @classmethod
    def find(cls, spec):
        """
        Find LocalStreams indicated by spec. Spec must by a filename that
        exists or a glob matching at least one filename.
        Return an iterable of LocalStreams for each matched name or raise
        ValueError.
        """
        if os.path.exists(spec):
            return cls(spec),

        # The filename didn't exist so assume it is a glob
        matches = glob.glob(spec)

        if not matches:
            msg = "Cannot find file (or expand pattern): '%s'" % spec
            raise ValueError(msg)

        # Otherwise, matches will be local filenames that exist
        return map(cls, matches)

    @property
    def url(self):
        return 'file:' + self.name

    @property
    def basename(self):
        return os.path.basename(urlparse(self.name).path)

    @contextlib.contextmanager
    def local_filename(self):
        """
        Return a filename on the local file system containing self.stream
        """
        yield self.name

    def sign(self, identity, sign_with):
        "Sign the dist"
        print("Signing {0}".format(self.basename))
        with self.local_filename() as filename:
            gpg_args = [sign_with, "--detach-sign", "-a", filename]
            if identity:
                gpg_args[2:2] = ["--local-user", identity]
            subprocess.check_call(gpg_args)
            with open(filename + '.asc', 'rb') as sig_stream:
                signature = sig_stream.read()
            # todo: consider removing signature
        return signature

    @property
    def stream(self):
        if not hasattr(self, '_stream'):
            with urlopen(self.url) as reader:
                self._stream = io.BytesIO(reader.read())
        self._stream.seek(0)
        return self._stream


class RemoteStream(LocalStream):
    """
    A file stream located in a remote location (e.g. HTTP)
    """
    @classmethod
    def find(cls, spec):
        """
        Find all streams indicated by spec. May be a URL, filename, or glob.

        Return an iterable of LocalStreams.
        """
        if not urlparse(spec).scheme:
            # it's a filename or glob
            return LocalStream.find(spec)
        return cls(spec),

    @property
    def url(self):
        return self.name

    @contextlib.contextmanager
    def local_filename(self):
        """
        Return a filename on the local file system containing self.stream
        """
        try:
            tf = tempfile.NamedTemporaryFile(suffix=self.basename,
                delete=False)
            with tf:
                tf.file.write(self.stream.getvalue())
            yield tf.name
        finally:
            os.remove(tf.name)


def upload(dists, repository, sign, identity, username, password, comment,
           sign_with):
    # Check that a nonsensical option wasn't given
    if not sign and identity:
        raise ValueError("sign must be given along with identity")

    # Determine if the user has passed in pre-signed distributions
    signatures = dict(
        (os.path.basename(d), d) for d in dists if d.endswith(".asc")
    )
    dists = itertools.chain.from_iterable(
        RemoteStream.find(spec)
        for spec in dists
        if not spec.endswith(".asc")
    )

    config = _load_config(repository)

    print("Uploading distributions to {0}".format(config["repository"]))

    auth = get_username(username, config), get_password(password, config)

    session = requests.session()
    session.auth = auth

    for dist in dists:
        _do_upload(dist, signatures, config, session, sign, comment, identity,
            sign_with)


def _load_config(repository):
    "Load config from ~/.pypirc"
    try:
        config = get_config()[repository]
    except KeyError:
        raise KeyError(
            "Missing '{0}' section from the configuration file".format(
                repository,
            ),
        )

    parsed = urlparse(config["repository"])
    if parsed.netloc in ["pypi.python.org", "testpypi.python.org"]:
        config["repository"] = urlunparse(
            ("https",) + parsed[1:]
        )
    return config


def _do_upload(dist, signatures, config, session, sign, comment, identity,
        sign_with):

    # Extract the metadata from the package
    for ext, dtype in DIST_EXTENSIONS.items():
        if dist.basename.endswith(ext):
            with dist.local_filename() as filename:
                meta = DIST_TYPES[dtype](filename)
            break
    else:
        raise ValueError(
            "Unknown distribution format: '%s'" % dist.basename
        )

    if dtype == "bdist_egg":
        with dist.local_filename() as filename:
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

    filedata = {
        "content": (dist.basename, dist.stream.getvalue()),
    }
    data["md5_digest"] = hashlib.md5(dist.stream.getvalue()).hexdigest()

    signed_name = dist.basename + ".asc"
    if signed_name in signatures:
        with open(signatures[signed_name], "rb") as gpg:
            filedata["gpg_signature"] = (signed_name, gpg.read())
    elif sign:
        signature = dist.sign(identity, sign_with)
        filedata["gpg_signature"] = (signed_name, signature)

    print("Uploading {dist.basename}".format(**vars()))

    resp = session.post(
        config["repository"],
        data=dict((k, v) for k, v in data.items() if v),
        files=filedata,
    )
    # Bug 28. Try to silence a ResourceWarning by releasing the socket and
    # clearing the connection pool.
    resp.close()
    session.close()
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
