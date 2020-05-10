"""
Verify that twine passes type-checking when used as a library.

https://mypy.readthedocs.io/en/stable/installed_packages.html#making-pep-561-compatible-packages
"""
import subprocess
import textwrap

import pytest


@pytest.fixture
def example_py(tmpdir, monkeypatch):
    # Changing directory so that mypy uses installed twine, instead of source
    monkeypatch.chdir(tmpdir)
    return tmpdir / "example.py"


def test_no_missing_import(example_py):
    example_py.write("""import twine""")

    subprocess.run(["mypy", "--strict", example_py], check=True)


def test_type_error_for_command(example_py):
    example_py.write(
        textwrap.dedent(
            """
            from twine.commands import check

            check.check('example.pkg')
            """
        )
    )

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        subprocess.run(
            ["mypy", "--strict", example_py], check=True, stdout=subprocess.PIPE
        )

    assert b"1 error in 1 file" in excinfo.value.output
    assert (
        b'"check" has incompatible type "str"; expected "List[str]"'
        in excinfo.value.output
    )


def test_type_error_for_class(example_py):
    example_py.write(
        textwrap.dedent(
            """
            from twine import repository

            repo = repository.Repository()
            """
        )
    )

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        subprocess.run(
            ["mypy", "--strict", example_py], check=True, stdout=subprocess.PIPE
        )

    assert b"1 error in 1 file" in excinfo.value.output
    assert b'Too few arguments for "Repository"' in excinfo.value.output
