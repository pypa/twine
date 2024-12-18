import os
import pathlib
import tarfile

import pytest

from twine import exceptions
from twine import sdist

from .helpers import TESTS_DIR
from .helpers import build_archive


@pytest.fixture(
    params=[
        "fixtures/twine-1.5.0.tar.gz",
        "fixtures/twine-1.6.5.tar.gz",
    ]
)
def example_sdist(request):
    file_name = os.path.join(TESTS_DIR, request.param)
    return sdist.SDist(file_name)


@pytest.fixture(params=["tar.gz", "zip"])
def archive_format(request):
    return request.param


def test_read_example(example_sdist):
    """Parse metadata from a valid sdist file."""
    metadata = example_sdist.read()
    assert b"Metadata-Version: 1.1" in metadata
    assert b"Name: twine" in metadata
    assert b"Version: 1." in metadata


def test_read_non_existent():
    """Raise an exception when sdist file doesn't exist."""
    file_name = str(pathlib.Path("/foo/bar/baz.tar.gz").resolve())
    with pytest.raises(exceptions.InvalidDistribution, match="No such file"):
        sdist.SDist(file_name).read()


def test_formar_not_supported():
    """Raise an exception when sdist is not a .tar.gz or a .zip."""
    file_name = str(pathlib.Path("/foo/bar/baz.foo").resolve())
    with pytest.raises(exceptions.InvalidDistribution, match="Unsupported sdist"):
        sdist.SDist(file_name).read()


def test_read(archive_format, tmp_path):
    """Read PKG-INFO from a valid sdist."""
    filepath = build_archive(
        tmp_path,
        "test-1.2.3",
        archive_format,
        {
            "test-1.2.3/README": "README",
            "test-1.2.3/PKG-INFO": """
                Metadata-Version: 1.1
                Name: test
                Version: 1.2.3
            """,
        },
    )

    metadata = sdist.SDist(str(filepath)).read()
    assert b"Metadata-Version: 1.1" in metadata
    assert b"Name: test" in metadata
    assert b"Version: 1.2.3" in metadata


def test_missing_pkg_info(archive_format, tmp_path):
    """Raise an exception when sdist does not contain PKG-INFO."""
    filepath = build_archive(
        tmp_path,
        "test-1.2.3",
        archive_format,
        {
            "test-1.2.3/README": "README",
        },
    )

    with pytest.raises(exceptions.InvalidDistribution, match="No PKG-INFO in archive"):
        sdist.SDist(str(filepath)).read()


def test_invalid_pkg_info(archive_format, tmp_path):
    """Raise an exception when PKG-INFO does not contain ``Metadata-Version``."""
    filepath = build_archive(
        tmp_path,
        "test-1.2.3",
        archive_format,
        {
            "test-1.2.3/README": "README",
            "test-1.2.3/PKG-INFO": """
                Name: test
                Version: 1.2.3.
             """,
        },
    )

    with pytest.raises(exceptions.InvalidDistribution, match="No PKG-INFO in archive"):
        sdist.SDist(str(filepath)).read()


def test_pkg_info_directory(archive_format, tmp_path):
    """Raise an exception when PKG-INFO is a directory."""
    filepath = build_archive(
        tmp_path,
        "test-1.2.3",
        archive_format,
        {
            "test-1.2.3/README": "README",
            "test-1.2.3/PKG-INFO/content": """
                Metadata-Version: 1.1
                Name: test
                Version: 1.2.3.
             """,
        },
    )

    with pytest.raises(exceptions.InvalidDistribution, match="No PKG-INFO in archive"):
        sdist.SDist(str(filepath)).read()


def test_pkg_info_not_regular_file(tmp_path):
    """Raise an exception when PKG-INFO is a directory."""
    link = tarfile.TarInfo()
    link.type = tarfile.LNKTYPE
    link.linkname = "README"

    filepath = build_archive(
        tmp_path,
        "test-1.2.3",
        "tar.gz",
        {
            "test-1.2.3/README": "README",
            "test-1.2.3/PKG-INFO": link,
        },
    )

    with pytest.raises(exceptions.InvalidDistribution, match="PKG-INFO is not a reg"):
        sdist.SDist(str(filepath)).read()


def test_multiple_top_level(archive_format, tmp_path):
    """Raise an exception when there are too many top-level members."""
    filepath = build_archive(
        tmp_path,
        "test-1.2.3",
        archive_format,
        {
            "test-1.2.3/README": "README",
            "test-1.2.3/PKG-INFO": """
                Metadata-Version: 1.1
                Name: test
                Version: 1.2.3.
             """,
            "test-2.0.0/README": "README",
        },
    )

    with pytest.raises(exceptions.InvalidDistribution, match="Too many top-level"):
        sdist.SDist(str(filepath)).read()


def test_py_version(example_sdist):
    assert example_sdist.py_version == "source"
