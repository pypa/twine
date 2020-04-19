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
from io import BytesIO
from textwrap import dedent
from zipfile import ZipFile

import pytest

from twine import exceptions
from twine import wheel


@pytest.fixture(
    params=[
        "fixtures/twine-1.5.0-py2.py3-none-any.whl",
        "alt-fixtures/twine-1.5.0-py2.py3-none-any.whl",
    ]
)
def example_wheel(request):
    file_name = os.path.join(os.path.dirname(__file__), request.param)
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
    with pytest.raises(exceptions.InvalidDistribution) as excinfo:
        wheel.Wheel(file_name)

    assert "Not a known archive format: {}".format(file_name) == str(excinfo.value)


def test_read_wheel_without_metadata(capsys, tmpdir):
    """Test reading a wheel file with empty metadata"""

    def create_empty_metadata_wheel(name, version):
        def add_file(path, text):
            contents = text.encode("utf-8")
            z.writestr(path, contents)
            records.append((path, text, str(len(text))))

        dist_info = "{}-{}.dist-info".format(name, version)
        record_path = "{}/RECORD".format(dist_info)
        records = []
        buf = BytesIO()
        with ZipFile(buf, "w") as z:
            add_file("{}/WHEEL".format(dist_info), "Wheel-Version: 1.0")
            add_file(
                "{}/METADATA".format(dist_info), dedent(""),
            )
            z.writestr(record_path, "\n".join(",".join(r) for r in records))
        buf.seek(0)
        return buf.read()

    wheel_data = create_empty_metadata_wheel("badwheel", "1.0")
    whl_file = tmpdir.mkdir("wheel").join("badwheel.whl")
    whl_file.write(wheel_data, mode="wb")

    with pytest.raises(exceptions.InvalidDistribution) as excinfo:
        wheel.Wheel(whl_file)

    assert "No METADATA in archive: {}".format(whl_file) == str(excinfo.value)
