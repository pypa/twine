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
import string

import pretend
import pytest

from twine import exceptions
from twine import package as package_file

from . import helpers


def test_sign_file(monkeypatch):
    replaced_check_call = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(package_file.subprocess, "check_call", replaced_check_call)
    filename = "tests/fixtures/deprecated-pypirc"

    package = package_file.PackageFile(
        filename=filename,
        comment=None,
        metadata=pretend.stub(name="deprecated-pypirc"),
        python_version=None,
        filetype=None,
    )
    try:
        package.sign("gpg2", None)
    except OSError:
        pass
    args = ("gpg2", "--detach-sign", "-a", filename)
    assert replaced_check_call.calls == [pretend.call(args)]


def test_sign_file_with_identity(monkeypatch):
    replaced_check_call = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(package_file.subprocess, "check_call", replaced_check_call)
    filename = "tests/fixtures/deprecated-pypirc"

    package = package_file.PackageFile(
        filename=filename,
        comment=None,
        metadata=pretend.stub(name="deprecated-pypirc"),
        python_version=None,
        filetype=None,
    )
    try:
        package.sign("gpg", "identity")
    except OSError:
        pass
    args = ("gpg", "--detach-sign", "--local-user", "identity", "-a", filename)
    assert replaced_check_call.calls == [pretend.call(args)]


def test_run_gpg_raises_exception_if_no_gpgs(monkeypatch):
    replaced_check_call = pretend.raiser(FileNotFoundError("not found"))
    monkeypatch.setattr(package_file.subprocess, "check_call", replaced_check_call)
    gpg_args = ("gpg", "--detach-sign", "-a", "pypircfile")

    with pytest.raises(exceptions.InvalidSigningExecutable) as err:
        package_file.PackageFile.run_gpg(gpg_args)

    assert "executables not available" in err.value.args[0]


def test_run_gpg_raises_exception_if_not_using_gpg(monkeypatch):
    replaced_check_call = pretend.raiser(FileNotFoundError("not found"))
    monkeypatch.setattr(package_file.subprocess, "check_call", replaced_check_call)
    gpg_args = ("not_gpg", "--detach-sign", "-a", "pypircfile")

    with pytest.raises(exceptions.InvalidSigningExecutable) as err:
        package_file.PackageFile.run_gpg(gpg_args)

    assert "not_gpg executable not available" in err.value.args[0]


def test_run_gpg_falls_back_to_gpg2(monkeypatch):
    def check_call(arg_list):
        if arg_list[0] == "gpg":
            raise FileNotFoundError("gpg not found")

    replaced_check_call = pretend.call_recorder(check_call)
    monkeypatch.setattr(package_file.subprocess, "check_call", replaced_check_call)
    gpg_args = ("gpg", "--detach-sign", "-a", "pypircfile")

    package_file.PackageFile.run_gpg(gpg_args)

    gpg2_args = replaced_check_call.calls[1].args
    assert gpg2_args[0][0] == "gpg2"


def test_package_signed_name_is_correct():
    filename = "tests/fixtures/deprecated-pypirc"

    package = package_file.PackageFile(
        filename=filename,
        comment=None,
        metadata=pretend.stub(name="deprecated-pypirc"),
        python_version=None,
        filetype=None,
    )

    assert package.signed_basefilename == "deprecated-pypirc.asc"
    assert package.signed_filename == (filename + ".asc")


@pytest.mark.parametrize(
    "pkg_name,expected_name",
    [
        (string.ascii_letters, string.ascii_letters),
        (string.digits, string.digits),
        (string.punctuation, "-.-"),
        ("mosaik.SimConfig", "mosaik.SimConfig"),
        ("mosaik$$$$.SimConfig", "mosaik-.SimConfig"),
    ],
)
def test_package_safe_name_is_correct(pkg_name, expected_name):
    package = package_file.PackageFile(
        filename="tests/fixtures/deprecated-pypirc",
        comment=None,
        metadata=pretend.stub(name=pkg_name),
        python_version=None,
        filetype=None,
    )

    assert package.safe_name == expected_name


def test_metadata_dictionary_keys():
    """Merge multiple sources of metadata into a single dictionary."""
    package = package_file.PackageFile.from_filename(helpers.SDIST_FIXTURE, None)
    assert set(package.metadata_dictionary()) == {
        # identify release
        "name",
        "version",
        # file content
        "filetype",
        "pyversion",
        # additional meta-data
        "metadata_version",
        "summary",
        "home_page",
        "author",
        "author_email",
        "maintainer",
        "maintainer_email",
        "license",
        "description",
        "keywords",
        "platform",
        "classifiers",
        "download_url",
        "supported_platform",
        "comment",
        "md5_digest",
        "sha256_digest",
        "blake2_256_digest",
        # PEP 314
        "provides",
        "requires",
        "obsoletes",
        # Metadata 1.2
        "project_urls",
        "provides_dist",
        "obsoletes_dist",
        "requires_dist",
        "requires_external",
        "requires_python",
        # Metadata 2.1
        "provides_extras",
        "description_content_type",
        # Metadata 2.2
        "dynamic",
    }


@pytest.mark.parametrize("gpg_signature", [(None), (pretend.stub())])
def test_metadata_dictionary_values(gpg_signature):
    """Pass values from pkginfo.Distribution through to dictionary."""
    meta = pretend.stub(
        name="whatever",
        version=pretend.stub(),
        metadata_version=pretend.stub(),
        summary=pretend.stub(),
        home_page=pretend.stub(),
        author=pretend.stub(),
        author_email=pretend.stub(),
        maintainer=pretend.stub(),
        maintainer_email=pretend.stub(),
        license=pretend.stub(),
        description=pretend.stub(),
        keywords=pretend.stub(),
        platforms=pretend.stub(),
        classifiers=pretend.stub(),
        download_url=pretend.stub(),
        supported_platforms=pretend.stub(),
        provides=pretend.stub(),
        requires=pretend.stub(),
        obsoletes=pretend.stub(),
        project_urls=pretend.stub(),
        provides_dist=pretend.stub(),
        obsoletes_dist=pretend.stub(),
        requires_dist=pretend.stub(),
        requires_external=pretend.stub(),
        requires_python=pretend.stub(),
        provides_extras=pretend.stub(),
        description_content_type=pretend.stub(),
        dynamic=pretend.stub(),
    )

    package = package_file.PackageFile(
        filename="tests/fixtures/twine-1.5.0-py2.py3-none-any.whl",
        comment=pretend.stub(),
        metadata=meta,
        python_version=pretend.stub(),
        filetype=pretend.stub(),
    )
    package.gpg_signature = gpg_signature

    result = package.metadata_dictionary()

    # identify release
    assert result["name"] == package.safe_name
    assert result["version"] == meta.version

    # file content
    assert result["filetype"] == package.filetype
    assert result["pyversion"] == package.python_version

    # additional meta-data
    assert result["metadata_version"] == meta.metadata_version
    assert result["summary"] == meta.summary
    assert result["home_page"] == meta.home_page
    assert result["author"] == meta.author
    assert result["author_email"] == meta.author_email
    assert result["maintainer"] == meta.maintainer
    assert result["maintainer_email"] == meta.maintainer_email
    assert result["license"] == meta.license
    assert result["description"] == meta.description
    assert result["keywords"] == meta.keywords
    assert result["platform"] == meta.platforms
    assert result["classifiers"] == meta.classifiers
    assert result["download_url"] == meta.download_url
    assert result["supported_platform"] == meta.supported_platforms
    assert result["comment"] == package.comment

    # PEP 314
    assert result["provides"] == meta.provides
    assert result["requires"] == meta.requires
    assert result["obsoletes"] == meta.obsoletes

    # Metadata 1.2
    assert result["project_urls"] == meta.project_urls
    assert result["provides_dist"] == meta.provides_dist
    assert result["obsoletes_dist"] == meta.obsoletes_dist
    assert result["requires_dist"] == meta.requires_dist
    assert result["requires_external"] == meta.requires_external
    assert result["requires_python"] == meta.requires_python

    # Metadata 2.1
    assert result["provides_extras"] == meta.provides_extras
    assert result["description_content_type"] == meta.description_content_type

    # Metadata 2.2
    assert result["dynamic"] == meta.dynamic

    # GPG signature
    assert result.get("gpg_signature") == gpg_signature


TWINE_1_5_0_WHEEL_HEXDIGEST = package_file.Hexdigest(
    "1919f967e990bee7413e2a4bc35fd5d1",
    "d86b0f33f0c7df49e888b11c43b417da5520cbdbce9f20618b1494b600061e67",
    "b657a4148d05bd0098c1d6d8cc4e14e766dbe93c3a5ab6723b969da27a87bac0",
)


def test_hash_manager():
    """Generate hexdigest via HashManager."""
    filename = "tests/fixtures/twine-1.5.0-py2.py3-none-any.whl"
    hasher = package_file.HashManager(filename)
    hasher.hash()
    assert hasher.hexdigest() == TWINE_1_5_0_WHEEL_HEXDIGEST


def test_fips_hash_manager_md5(monkeypatch):
    """Generate hexdigest without MD5 when hashlib is using FIPS mode."""
    replaced_md5 = pretend.raiser(ValueError("fipsmode"))
    monkeypatch.setattr(package_file.hashlib, "md5", replaced_md5)

    filename = "tests/fixtures/twine-1.5.0-py2.py3-none-any.whl"
    hasher = package_file.HashManager(filename)
    hasher.hash()
    hashes = TWINE_1_5_0_WHEEL_HEXDIGEST._replace(md5=None)
    assert hasher.hexdigest() == hashes


@pytest.mark.parametrize("exception_class", [TypeError, ValueError])
def test_fips_hash_manager_blake2(exception_class, monkeypatch):
    """Generate hexdigest without BLAKE2 when hashlib is using FIPS mode."""
    replaced_blake2b = pretend.raiser(exception_class("fipsmode"))
    monkeypatch.setattr(package_file.hashlib, "blake2b", replaced_blake2b)

    filename = "tests/fixtures/twine-1.5.0-py2.py3-none-any.whl"
    hasher = package_file.HashManager(filename)
    hasher.hash()
    hashes = TWINE_1_5_0_WHEEL_HEXDIGEST._replace(blake2=None)
    assert hasher.hexdigest() == hashes


def test_fips_metadata_excludes_md5_and_blake2(monkeypatch):
    """Generate a valid metadata dictionary for Nexus when FIPS is enabled.

    See also: https://github.com/pypa/twine/issues/775
    """
    replaced_blake2b = pretend.raiser(ValueError("fipsmode"))
    replaced_md5 = pretend.raiser(ValueError("fipsmode"))
    monkeypatch.setattr(package_file.hashlib, "md5", replaced_md5)
    monkeypatch.setattr(package_file.hashlib, "blake2b", replaced_blake2b)

    filename = "tests/fixtures/twine-1.5.0-py2.py3-none-any.whl"
    pf = package_file.PackageFile.from_filename(filename, None)

    mddict = pf.metadata_dictionary()
    assert "md5_digest" not in mddict
    assert "blake2_256_digest" not in mddict


@pytest.mark.parametrize(
    "read_data, missing_fields",
    [
        pytest.param(
            b"Metadata-Version: 2.3\nName: test-package\nVersion: 1.0.0\n",
            "Name, Version",
            id="unsupported Metadata-Version",
        ),
        pytest.param(
            b"Metadata-Version: 2.2\nName: UNKNOWN\nVersion: UNKNOWN\n",
            "Name, Version",
            id="missing Name and Version",
        ),
        pytest.param(
            b"Metadata-Version: 2.2\nName: UNKNOWN\nVersion: 1.0.0\n",
            "Name",
            id="missing Name",
        ),
        pytest.param(
            b"Metadata-Version: 2.2\nName: test-package\nVersion: UNKNOWN\n",
            "Version",
            id="missing Version",
        ),
    ],
)
def test_pkginfo_returns_no_metadata(read_data, missing_fields, monkeypatch):
    """Raise an exception when pkginfo can't interpret the metadata.

    This could be caused by a version number or format it doesn't support yet.
    """
    monkeypatch.setattr(package_file.wheel.Wheel, "read", lambda _: read_data)
    filename = "tests/fixtures/twine-1.5.0-py2.py3-none-any.whl"

    with pytest.raises(exceptions.InvalidDistribution) as err:
        package_file.PackageFile.from_filename(filename, comment=None)

    assert (
        f"Metadata is missing required fields: {missing_fields}." in err.value.args[0]
    )
    assert "1.0, 1.1, 1.2, 2.0, 2.1, 2.2" in err.value.args[0]


def test_malformed_from_file(monkeypatch):
    """Raise an exception when malformed package file triggers EOFError."""
    filename = "tests/fixtures/malformed.tar.gz"

    with pytest.raises(exceptions.InvalidDistribution) as err:
        package_file.PackageFile.from_filename(filename, comment=None)

    assert "Invalid distribution file" in err.value.args[0]


def test_package_from_egg():
    filename = "tests/fixtures/twine-3.3.0-py3.9.egg"
    package_file.PackageFile.from_filename(filename, comment=None)
