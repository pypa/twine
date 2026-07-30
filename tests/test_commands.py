import dataclasses
import os

import pytest

from twine import commands
from twine import exceptions


def test_ensure_wheel_files_uploaded_first():
    files = commands._group_wheel_files_first(
        ["twine/foo.py", "twine/first.whl", "twine/bar.py", "twine/second.whl"]
    )
    expected = [
        "twine/first.whl",
        "twine/second.whl",
        "twine/foo.py",
        "twine/bar.py",
    ]
    assert expected == files


def test_ensure_if_no_wheel_files():
    files = commands._group_wheel_files_first(["twine/foo.py", "twine/bar.py"])
    expected = ["twine/foo.py", "twine/bar.py"]
    assert expected == files


def test_find_dists_expands_globs():
    files = sorted(commands._find_dists(["twine/__*.py"]))
    expected = [
        os.path.join("twine", "__init__.py"),
        os.path.join("twine", "__main__.py"),
    ]
    assert expected == files


def test_find_dists_errors_on_invalid_globs():
    with pytest.raises(exceptions.InvalidDistribution):
        commands._find_dists(["twine/*.rb"])


def test_find_dists_handles_real_files():
    expected = [
        "twine/__init__.py",
        "twine/__main__.py",
        "twine/cli.py",
        "twine/utils.py",
        "twine/wheel.py",
    ]
    files = commands._find_dists(expected)
    assert expected == files


class Signed(str):

    @property
    def signature(self):
        return f"{self}.asc"

    def attestation(self, what):
        return f"{self}.{what}.attestation"


@dataclasses.dataclass
class Distribution:
    name: str
    version: str

    @property
    def sdist(self):
        return Signed(f"dist/{self.name}-{self.version}.tar.gz")

    @property
    def wheel(self):
        return Signed(f"dist/{self.name}-{self.version}-py2.py3-none-any.whl")


def test_split_inputs():
    """Split inputs into dists, signatures, and attestations."""
    a = Distribution("twine", "1.5.0")
    b = Distribution("twine", "1.6.5")

    inputs = [
        a.wheel,
        a.wheel.signature,
        a.wheel.attestation("build"),
        a.wheel.attestation("build.publish"),
        a.sdist,
        a.sdist.signature,
        b.wheel,
        b.wheel.attestation("frob"),
        b.sdist,
    ]

    inputs = commands._split_inputs(inputs)

    assert inputs.dists == [
        a.wheel,
        a.sdist,
        b.wheel,
        b.sdist,
    ]

    assert inputs.signatures == {
        "twine-1.5.0-py2.py3-none-any.whl.asc": a.wheel.signature,
        "twine-1.5.0.tar.gz.asc": a.sdist.signature,
    }

    assert inputs.attestations_by_dist == {
        a.wheel: [
            a.wheel.attestation("build"),
            a.wheel.attestation("build.publish"),
        ],
        a.sdist: [],
        b.wheel: [
            b.wheel.attestation("frob"),
        ],
        b.sdist: [],
    }
