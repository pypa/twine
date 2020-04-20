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
import os
from zipfile import ZipFile

import pytest
from tests.conftest import TESTS_DIR

from twine import exceptions
from twine import wheel


@pytest.fixture(
    params=[
        "fixtures/twine-1.5.0-py2.py3-none-any.whl",
        "alt-fixtures/twine-1.5.0-py2.py3-none-any.whl",
    ]
)
def example_wheel(request):
    file_name = os.path.join(TESTS_DIR, request.param)
    return wheel.Wheel(file_name)


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


def test_read_valid(example_wheel):
    """Test reading a valid wheel file"""
    metadata = example_wheel.read().decode().splitlines()
    assert "Name: twine" in metadata
    assert "Version: 1.5.0" in metadata


def test_read_non_existent_wheel_file_name():
    """Test reading a wheel file which doesn't exist"""

    file_name = "/foo/bar/baz.whl"
    with pytest.raises(exceptions.InvalidDistribution) as excinfo:
        wheel.Wheel(file_name)

    assert "No such file: {}".format(file_name) == str(excinfo.value)


def test_read_invalid_wheel_extension():
    """Test reading a wheel file without a .whl extension"""

    file_name = os.path.join(os.path.dirname(__file__), "fixtures/twine-1.5.0.tar.gz")
    with pytest.raises(
        exceptions.InvalidDistribution, match=f"Not a known archive format: {file_name}"
    ):
        wheel.Wheel(file_name)


def test_read_wheel_empty_metadata(tmpdir):
    """Test reading a wheel file with an empty METADATA file"""

    whl_file = tmpdir.mkdir("wheel").join("not-a-wheel.whl")
    with ZipFile(whl_file, "w") as zip_file:
        zip_file.writestr("METADATA", "")

    with pytest.raises(
        exceptions.InvalidDistribution, match=f"No METADATA in archive: {whl_file}"
    ):
        wheel.Wheel(whl_file)
