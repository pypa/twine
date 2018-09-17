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
from __future__ import unicode_literals

import sys

from twine.cli import dispatch
import twine.exceptions


def main():
    try:
        return dispatch(sys.argv[1:])
    except twine.exceptions.TwineException as exc:
        return '{0}: {1}'.format(
            exc.__class__.__name__,
            exc.args[0],
        )


if __name__ == "__main__":
    sys.exit(main())
