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
import pytest

from twine import wheel


@pytest.fixture(
    params=[
        "tests/fixtures/twine-1.5.0-py2.py3-none-any.whl",
        "tests/alt-fixtures/twine-1.5.0-py2.py3-none-any.whl",
    ]
)
def example_wheel(request):
    return wheel.Wheel(request.param)


def test_version_parsing(example_wheel):
    assert example_wheel.py_version == "py2.py3"


def test_find_metadata_files():
    names = [
        "package/lib/__init__.py",
        "package/lib/version.py",
        "package/METADATA.txt",
        "package/METADATA.json",
        "package/METADATA",
    ]
    expected = [
        ["package", "METADATA"],
        ["package", "METADATA.json"],
        ["package", "METADATA.txt"],
    ]
    candidates = wheel.Wheel.find_candidate_metadata_files(names)
    assert expected == candidates
