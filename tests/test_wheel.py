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
import pathlib
import re
import zipfile

import pretend
import pytest

from twine import exceptions
from twine import wheel

from . import helpers


@pytest.fixture(
    params=[
        "fixtures/twine-1.5.0-py2.py3-none-any.whl",
        "alt-fixtures/twine-1.5.0-py2.py3-none-any.whl",
    ]
)
def example_wheel(request):
    file_name = os.path.join(helpers.TESTS_DIR, request.param)
    return wheel.Wheel(file_name)


def test_version_parsing(example_wheel):
    assert example_wheel.py_version == "py2.py3"


def test_version_parsing_missing_pyver(monkeypatch, example_wheel):

    wheel.wheel_file_re = pretend.stub(match=lambda a: None)
    assert example_wheel.py_version == "any"


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
    """Parse metadata from a valid wheel file."""
    metadata = example_wheel.read().decode().splitlines()
    assert "Name: twine" in metadata
    assert "Version: 1.5.0" in metadata


def test_read_non_existent_wheel_file_name():
    """Raise an exception when wheel file doesn't exist."""
    file_name = str(pathlib.Path("/foo/bar/baz.whl").resolve())
    with pytest.raises(
        exceptions.InvalidDistribution, match=re.escape(f"No such file: {file_name}")
    ):
        wheel.Wheel(file_name)


def test_read_invalid_wheel_extension():
    """Raise an exception when file is missing .whl extension."""
    file_name = str(pathlib.Path(__file__).parent / "fixtures" / "twine-1.5.0.tar.gz")
    with pytest.raises(
        exceptions.InvalidDistribution,
        match=re.escape(f"Not a known archive format for file: {file_name}"),
    ):
        wheel.Wheel(file_name)


def test_read_wheel_empty_metadata(tmpdir):
    """Raise an exception when a wheel file is missing METADATA."""
    whl_file = tmpdir.mkdir("wheel").join("not-a-wheel.whl")
    with zipfile.ZipFile(whl_file, "w") as zip_file:
        zip_file.writestr("METADATA", "")

    with pytest.raises(
        exceptions.InvalidDistribution,
        match=re.escape(f"No METADATA in archive: {whl_file}"),
    ):
        wheel.Wheel(whl_file)
