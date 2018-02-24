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

import os
from lxml import objectify

try:
    from StringIO import StringIO
except ImportError:
    from _io import StringIO

from pkginfo import distribution
from pkginfo.distribution import Distribution

# Monkeypatch Metadata 2.0 support
distribution.HEADER_ATTRS_2_0 = distribution.HEADER_ATTRS_1_2
distribution.HEADER_ATTRS.update({"2.0": distribution.HEADER_ATTRS_2_0})


def try_decode(s):
    if isinstance(s, bytes):
        return s.decode('utf8')
    return s


class Ivy(Distribution):

    def __init__(self, filename, metadata_version=None):
        self.filename = filename
        self.basefilename = os.path.basename(self.filename)
        self.metadata_version = metadata_version
        self.extractMetadata()

    @property
    def py_version(self):
        return "any"

    def read(self):
        fqn = os.path.abspath(os.path.normpath(self.filename))
        if not os.path.exists(fqn):
            raise ValueError('No such file: %s' % fqn)

        if not fqn.endswith('.ivy'):
            raise ValueError('Not a known archive format: %s' % fqn)

        with open(fqn, "r") as xml_file:
            xml_string = xml_file.read()
            root = objectify.fromstring(xml_string)
            self.name = root["info"].get("module")
            self.version = root["info"].get("revision")
            return root["info"].get("revision")

    def parse(self, data):
        super(Ivy, self).parse(data)

        fp = StringIO(distribution.must_decode(data))
        msg = distribution.parse(fp)
        self.description = msg.get_payload()
