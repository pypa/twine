from twine import wheel

import pytest


@pytest.fixture(params=[
    'tests/fixtures/twine-1.5.0-py2.py3-none-any.whl',
    'tests/alt-fixtures/twine-1.5.0-py2.py3-none-any.whl'
])
def example_wheel(request):
    return wheel.Wheel(request.param)


def test_version_parsing(example_wheel):
    assert example_wheel.py_version == 'py2.py3'


def test_find_metadata_files():
    names = [
        'package/lib/__init__.py',
        'package/lib/version.py',
        'package/METADATA.txt',
        'package/METADATA.json',
        'package/METADATA',
    ]
    expected = [
        ['package', 'METADATA'],
        ['package', 'METADATA.json'],
        ['package', 'METADATA.txt'],
    ]
    candidates = wheel.Wheel.find_candidate_metadata_files(names)
    assert expected == candidates
