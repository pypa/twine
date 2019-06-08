from __future__ import unicode_literals

import pytest
import pretend

from twine.commands import register
from twine import exceptions


# TODO: Copied from test_upload.py. Extract to helpers?

WHEEL_FIXTURE = 'tests/fixtures/twine-1.5.0-py2.py3-none-any.whl'


def test_exception_for_redirect(make_settings):
    register_settings = make_settings("""
        [pypi]
        repository: https://test.pypi.org/legacy
        username:foo
        password:bar
    """)

    stub_response = pretend.stub(
        is_redirect=True,
        status_code=301,
        headers={'location': 'https://test.pypi.org/legacy/'}
    )

    stub_repository = pretend.stub(
        register=lambda package: stub_response,
        close=lambda: None
    )

    register_settings.create_repository = lambda: stub_repository

    with pytest.raises(exceptions.RedirectDetected) as err:
        register.register(register_settings, WHEEL_FIXTURE)

    assert "https://test.pypi.org/legacy/" in err.value.args[0]
