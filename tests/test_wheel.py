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
import pathlib
import zipfile

import pytest

from twine import exceptions
from twine import wheel


@pytest.fixture()
def example_wheel(request):
    parent = pathlib.Path(__file__).parent
    file_name = str(parent / "fixtures" / "twine-1.5.0-py2.py3-none-any.whl")
    return wheel.Wheel(file_name)


def test_version_parsing(example_wheel):
    assert example_wheel.py_version == "py2.py3"


@pytest.mark.parametrize(
    "file_name,valid",
    [
        ("name-1.2.3-py313-none-any.whl", True),
        ("name-1.2.3-42-py313-none-any.whl", True),
        ("long_name-1.2.3-py3-none-any.whl", True),
        ("missing_components-1.2.3.whl", False),
    ],
)
def test_parse_wheel_file_name(file_name, valid):
    assert bool(wheel.wheel_file_re.match(file_name)) == valid


def test_invalid_file_name(monkeypatch):
    parent = pathlib.Path(__file__).parent
    file_name = str(parent / "fixtures" / "twine-1.5.0-py2.whl")
    with pytest.raises(exceptions.InvalidDistribution, match="Invalid wheel filename"):
        wheel.Wheel(file_name)


def test_read_valid(example_wheel):
    """Parse metadata from a valid wheel file."""
    metadata = example_wheel.read().decode().splitlines()
    assert "Name: twine" in metadata
    assert "Version: 1.5.0" in metadata


def test_read_non_existent_wheel_file_name():
    """Raise an exception when wheel file doesn't exist."""
    file_name = str(pathlib.Path("/foo/bar/baz-1.2.3-py3-none-any.whl").resolve())
    with pytest.raises(exceptions.InvalidDistribution, match="No such file"):
        wheel.Wheel(file_name).read()


def test_read_invalid_wheel_extension():
    """Raise an exception when file is missing .whl extension."""
    file_name = str(pathlib.Path(__file__).parent / "fixtures" / "twine-1.5.0.tar.gz")
    with pytest.raises(exceptions.InvalidDistribution, match="Invalid wheel filename"):
        wheel.Wheel(file_name).read()


def test_read_wheel_missing_metadata(example_wheel, monkeypatch):
    """Raise an exception when a wheel file is missing METADATA."""

    def patch(self, name):
        raise KeyError

    monkeypatch.setattr(zipfile.ZipFile, "read", patch)
    parent = pathlib.Path(__file__).parent
    file_name = str(parent / "fixtures" / "twine-1.5.0-py2.py3-none-any.whl")
    with pytest.raises(exceptions.InvalidDistribution, match="No METADATA in archive"):
        wheel.Wheel(file_name).read()


def test_read_wheel_empty_metadata(example_wheel, monkeypatch):
    """Raise an exception when a wheel file is missing METADATA."""
    monkeypatch.setattr(zipfile.ZipFile, "read", lambda self, name: b"")
    parent = pathlib.Path(__file__).parent
    file_name = str(parent / "fixtures" / "twine-1.5.0-py2.py3-none-any.whl")
    with pytest.raises(exceptions.InvalidDistribution, match="No METADATA in archive"):
        wheel.Wheel(file_name).read()
