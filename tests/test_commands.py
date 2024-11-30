import os

import pytest

from tests import helpers
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


def test_split_inputs():
    """Split inputs into dists, signatures, and attestations."""
    inputs = [
        helpers.WHEEL_FIXTURE,
        helpers.WHEEL_FIXTURE + ".asc",
        helpers.WHEEL_FIXTURE + ".build.attestation",
        helpers.WHEEL_FIXTURE + ".publish.attestation",
        helpers.SDIST_FIXTURE,
        helpers.SDIST_FIXTURE + ".asc",
        helpers.NEW_WHEEL_FIXTURE,
        helpers.NEW_WHEEL_FIXTURE + ".frob.attestation",
        helpers.NEW_SDIST_FIXTURE,
    ]

    inputs = commands._split_inputs(inputs)

    assert inputs.dists == [
        helpers.WHEEL_FIXTURE,
        helpers.SDIST_FIXTURE,
        helpers.NEW_WHEEL_FIXTURE,
        helpers.NEW_SDIST_FIXTURE,
    ]

    expected_signatures = {
        os.path.basename(dist) + ".asc": dist + ".asc"
        for dist in [helpers.WHEEL_FIXTURE, helpers.SDIST_FIXTURE]
    }
    assert inputs.signatures == expected_signatures

    assert inputs.attestations_by_dist == {
        helpers.WHEEL_FIXTURE: [
            helpers.WHEEL_FIXTURE + ".build.attestation",
            helpers.WHEEL_FIXTURE + ".publish.attestation",
        ],
        helpers.SDIST_FIXTURE: [],
        helpers.NEW_WHEEL_FIXTURE: [helpers.NEW_WHEEL_FIXTURE + ".frob.attestation"],
        helpers.NEW_SDIST_FIXTURE: [],
    }
