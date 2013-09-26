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

import distutils.config


def get_distutils_config(repository):
    pypicmd = distutils.config.PyPIRCCommand
    pypicmd.announce = lambda msg: msg

    class Fake(object):

        DEFAULT_REPOSITORY = "http://pypi.python.org/pypi"
        DEFAULT_REALM = "pypi"
        repository = None
        realm = None

        def announce(self, msg):
            pass

        def _get_rc_file(self):
            return pypicmd._get_rc_file(self)

    self = Fake()
    self.repository = repository

    return pypicmd._read_pypirc(self)
