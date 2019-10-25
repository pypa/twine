# Copyright 2015 Ian Cordasco
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
from typing import Dict, IO, Optional, Union, Sequence, Tuple

import collections
import hashlib
import io
import os
import subprocess
from hashlib import blake2b

import pkginfo
import pkg_resources

from twine.wheel import Wheel
from twine.wininst import WinInst
from twine import exceptions

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

MetadataValue = Union[str, Sequence[str], Tuple[str, IO, str]]


class PackageFile:
    def __init__(
        self,
        filename: str,
        comment: Optional[str],
        metadata: pkginfo.Distribution,
        python_version: Optional[str],
        filetype: Optional[str],
    ) -> None:
        self.filename = filename
        self.basefilename = os.path.basename(filename)
        self.comment = comment
        self.metadata = metadata
        self.python_version = python_version
        self.filetype = filetype
        self.safe_name = pkg_resources.safe_name(metadata.name)
        self.signed_filename = self.filename + '.asc'
        self.signed_basefilename = self.basefilename + '.asc'
        self.gpg_signature: Optional[Tuple[str, bytes]] = None

        hasher = HashManager(filename)
        hasher.hash()
        hexdigest = hasher.hexdigest()

        self.md5_digest = hexdigest.md5
        self.sha2_digest = hexdigest.sha2
        self.blake2_256_digest = hexdigest.blake2

    @classmethod
    def from_filename(cls, filename: str, comment: None) -> 'PackageFile':
        # Extract the metadata from the package
        for ext, dtype in DIST_EXTENSIONS.items():
            if filename.endswith(ext):
                meta = DIST_TYPES[dtype](filename)
                break
        else:
            raise exceptions.InvalidDistribution(
                "Unknown distribution format: '%s'" %
                os.path.basename(filename)
            )

        # If pkginfo encounters a metadata version it doesn't support, it may
        # give us back empty metadata. At the very least, we should have a name
        # and version
        if not (meta.name and meta.version):
            raise exceptions.InvalidDistribution(
                "Invalid distribution metadata. Try upgrading twine if "
                "possible."
            )

        py_version: Optional[str]
        if dtype == "bdist_egg":
            pkgd = pkg_resources.Distribution.from_filename(filename)
            py_version = pkgd.py_version
        elif dtype == "bdist_wheel":
            py_version = meta.py_version
        elif dtype == "bdist_wininst":
            py_version = meta.py_version
        else:
            py_version = None

        return cls(filename, comment, meta, py_version, dtype)

    def metadata_dictionary(self) -> Dict[str, MetadataValue]:
        meta = self.metadata
        data = {
            # identify release
            "name": self.safe_name,
            "version": meta.version,

            # file content
            "filetype": self.filetype,
            "pyversion": self.python_version,

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
            "comment": self.comment,
            "md5_digest": self.md5_digest,
            "sha256_digest": self.sha2_digest,
            "blake2_256_digest": self.blake2_256_digest,

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

            # Metadata 2.1
            "provides_extras": meta.provides_extras,
            "description_content_type": meta.description_content_type,
        }

        if self.gpg_signature is not None:
            data['gpg_signature'] = self.gpg_signature

        return data

    def add_gpg_signature(
        self,
        signature_filepath: str,
        signature_filename: str
    ):
        if self.gpg_signature is not None:
            raise exceptions.InvalidDistribution(
                'GPG Signature can only be added once'
            )

        with open(signature_filepath, "rb") as gpg:
            self.gpg_signature = (signature_filename, gpg.read())

    def sign(self, sign_with: str, identity: Optional[str]):
        print(f"Signing {self.basefilename}")
        gpg_args: Tuple[str, ...] = (sign_with, "--detach-sign")
        if identity:
            gpg_args += ("--local-user", identity)
        gpg_args += ("-a", self.filename)
        self.run_gpg(gpg_args)

        self.add_gpg_signature(self.signed_filename, self.signed_basefilename)

    @classmethod
    def run_gpg(cls, gpg_args):
        try:
            subprocess.check_call(gpg_args)
            return
        except FileNotFoundError:
            if gpg_args[0] != "gpg":
                raise exceptions.InvalidSigningExecutable(
                    "{} executable not available.".format(gpg_args[0]))

        print("gpg executable not available. Attempting fallback to gpg2.")
        try:
            subprocess.check_call(("gpg2",) + gpg_args[1:])
        except FileNotFoundError:
            print("gpg2 executable not available.")
            raise exceptions.InvalidSigningExecutable(
                "'gpg' or 'gpg2' executables not available. "
                "Try installing one of these or specifying an executable "
                "with the --sign-with flag."
            )


Hexdigest = collections.namedtuple('Hexdigest', ['md5', 'sha2', 'blake2'])


class HashManager:
    """Manage our hashing objects for simplicity.

    This will also allow us to better test this logic.
    """

    def __init__(self, filename: str) -> None:
        """Initialize our manager and hasher objects."""
        self.filename = filename

        self._md5_hasher = None
        try:
            self._md5_hasher = hashlib.md5()
        except ValueError:
            # FIPs mode disables MD5
            pass

        self._sha2_hasher = hashlib.sha256()

        self._blake_hasher = None
        if blake2b is not None:
            self._blake_hasher = blake2b(digest_size=256 // 8)

    def _md5_update(self, content: bytes) -> None:
        if self._md5_hasher is not None:
            self._md5_hasher.update(content)

    def _md5_hexdigest(self) -> Optional[str]:
        if self._md5_hasher is not None:
            return self._md5_hasher.hexdigest()
        return None

    def _sha2_update(self, content: bytes) -> None:
        if self._sha2_hasher is not None:
            self._sha2_hasher.update(content)

    def _sha2_hexdigest(self) -> Optional[str]:
        if self._sha2_hasher is not None:
            return self._sha2_hasher.hexdigest()
        return None

    def _blake_update(self, content: bytes) -> None:
        if self._blake_hasher is not None:
            self._blake_hasher.update(content)

    def _blake_hexdigest(self) -> Optional[str]:
        if self._blake_hasher is not None:
            return self._blake_hasher.hexdigest()
        return None

    def hash(self) -> None:
        """Hash the file contents."""
        with open(self.filename, "rb") as fp:
            for content in iter(lambda: fp.read(io.DEFAULT_BUFFER_SIZE), b''):
                self._md5_update(content)
                self._sha2_update(content)
                self._blake_update(content)

    def hexdigest(self) -> Hexdigest:
        """Return the hexdigest for the file."""
        return Hexdigest(
            self._md5_hexdigest(),
            self._sha2_hexdigest(),
            self._blake_hexdigest(),
        )
