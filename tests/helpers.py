# Copyright 2016 Ian Cordasco
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
"""Test functions useful across twine's tests."""

import os
import pathlib

TESTS_DIR = pathlib.Path(__file__).parent
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")
SDIST_FIXTURE = os.path.join(FIXTURES_DIR, "twine-1.5.0.tar.gz")
WHEEL_FIXTURE = os.path.join(FIXTURES_DIR, "twine-1.5.0-py2.py3-none-any.whl")
NEW_SDIST_FIXTURE = os.path.join(FIXTURES_DIR, "twine-1.6.5.tar.gz")
NEW_WHEEL_FIXTURE = os.path.join(FIXTURES_DIR, "twine-1.6.5-py2.py3-none-any.whl")
