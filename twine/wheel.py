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
import os
import re
import zipfile
from contextlib import suppress

from twine import distribution
from twine import exceptions

wheel_file_re = re.compile(
    r"""^(?P<name>[^-]+)-
         (?P<version>[^-]+)
         (:?-(?P<build>\d[^-]*))?-
         (?P<pyver>[^-]+)-
         (?P<abi>[^-]+)-
         (?P<plat>[^-]+)
         \.whl$""",
    re.VERBOSE,
)


class Wheel(distribution.Distribution):
    def __init__(self, filename: str) -> None:
        m = wheel_file_re.match(os.path.basename(filename))
        if not m:
            raise exceptions.InvalidDistribution(f"Invalid wheel filename: {filename}")
        self.name = m.group("name")
        self.version = m.group("version")
        self.pyver = m.group("pyver")

        if not os.path.exists(filename):
            raise exceptions.InvalidDistribution(f"No such file: {filename}")
        self.filename = filename

    @property
    def py_version(self) -> str:
        return self.pyver

    def read(self) -> bytes:
        with zipfile.ZipFile(self.filename) as wheel:
            with suppress(KeyError):
                # The wheel needs to contain the METADATA file at this location.
                data = wheel.read(f"{self.name}-{self.version}.dist-info/METADATA")
                if b"Metadata-Version" in data:
                    return data
        raise exceptions.InvalidDistribution(
            "No METADATA in archive or "
            f"METADATA missing 'Metadata-Version': {self.filename}"
        )
