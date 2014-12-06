import pytest

from twine.commands import upload


def test_find_dists_expands_globs():
    files = sorted(upload.find_dists(['twine/__*.py']))
    expected = ['twine/__init__.py', 'twine/__main__.py']
    assert expected == files


def test_find_dists_errors_on_invalid_globs():
    with pytest.raises(ValueError):
        upload.find_dists(['twine/*.rb'])


def test_find_dists_handles_real_files():
    expected = ['twine/__init__.py', 'twine/__main__.py', 'twine/cli.py',
                'twine/utils.py', 'twine/wheel.py']
    files = upload.find_dists(expected)
    assert expected == files
