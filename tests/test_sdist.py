import os
import pathlib
import re
import tarfile

import pretend
import pytest

from twine import exceptions
from twine import sdist

from . import helpers


@pytest.fixture(
    params=[
        "fixtures/twine-1.5.0.tar.gz",
        "fixtures/twine-1.6.5.tar.gz",
    ]
)
def example_sdist(request):
    file_name = os.path.join(helpers.TESTS_DIR, request.param)
    return sdist.SDist(file_name)


def test_read_valid(example_sdist):
    """Parse metadata from a valid sdist file."""
    metadata = example_sdist.read()
    assert b"Metadata-Version: 1.1" in metadata
    assert b"Name: twine" in metadata
    assert b"Version: 1." in metadata


def test_read_non_existent():
    """Raise an exception when sdist file doesn't exist."""
    file_name = str(pathlib.Path("/foo/bar/baz.tar.gz").resolve())
    with pytest.raises(
        exceptions.InvalidDistribution, match=re.escape(f"No such file: {file_name}")
    ):
        sdist.SDist(file_name).read()


def test_no_metadata(monkeypatch):
    """Raise an exception when sdist does not contain PKG-INFO."""
    file_name = os.path.join(helpers.TESTS_DIR, "fixtures/twine-1.5.0.tar.gz")
    monkeypatch.setattr(tarfile.TarFile, "getmembers", lambda x: [])
    with pytest.raises(
        exceptions.InvalidDistribution, match=re.escape("No PKG-INFO in archive")
    ):
        sdist.SDist(file_name).read()


def test_invalid_metadata(monkeypatch):
    """Raise an exception when PKG-INFO does not contain ``Metadata-Version``."""
    monkeypatch.setattr(
        tarfile.TarFile, "extractfile", lambda x, m: pretend.stub(read=lambda: b"")
    )
    file_name = os.path.join(helpers.TESTS_DIR, "fixtures/twine-1.5.0.tar.gz")
    with pytest.raises(
        exceptions.InvalidDistribution, match=re.escape("No PKG-INFO in archive")
    ):
        sdist.SDist(file_name).read()


def test_multiple_pkginfo(monkeypatch):
    """Find the right PKG-INFO."""
    file_name = os.path.join(helpers.TESTS_DIR, "fixtures/twine-1.5.0.tar.gz")
    getmembers = tarfile.TarFile.getmembers

    def patch(self):
        return [
            pretend.stub(name="twine-1.5.0/twine/PKG-INFO"),
            *getmembers(self),
            pretend.stub(name="twine-1.5.0/examples/PKG-INFO"),
        ]

    monkeypatch.setattr(tarfile.TarFile, "getmembers", patch)
    metadata = sdist.SDist(file_name).read()
    assert b"Metadata-Version: 1.1" in metadata
    assert b"Name: twine" in metadata
    assert b"Version: 1.5.0" in metadata


def test_py_version(example_sdist):
    assert example_sdist.py_version == "source"
