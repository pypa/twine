import os
from pathlib import Path

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


def test_find_dists_groups_artifacts_by_distribution(tmp_path):
    for filename in [
        "bar-0.0.2-py3-none-any.whl",
        "buzz-0.0.3-py3-none-any.whl",
        "foo-0.0.1-py3-none-any.whl",
        "bar-0.0.2.tar.gz",
        "buzz-0.0.3.tar.gz",
        "foo-0.0.1.tar.gz",
    ]:
        (tmp_path / filename).write_text("artifact")

    files = commands._find_dists([str(tmp_path / "*")])

    assert [Path(filename).name for filename in files] == [
        "bar-0.0.2-py3-none-any.whl",
        "bar-0.0.2.tar.gz",
        "buzz-0.0.3-py3-none-any.whl",
        "buzz-0.0.3.tar.gz",
        "foo-0.0.1-py3-none-any.whl",
        "foo-0.0.1.tar.gz",
    ]


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
