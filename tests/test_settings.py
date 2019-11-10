"""Tests for the Settings class and module."""
import os.path
import textwrap

from twine import exceptions
from twine import settings

import pytest


def test_settings_takes_no_positional_arguments():
    """Verify that the Settings initialization is kw-only."""
    with pytest.raises(TypeError):
        settings.Settings('a', 'b', 'c')


def test_settings_transforms_config(tmpdir):
    """Verify that the settings object transforms the passed in options."""
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(textwrap.dedent("""
            [pypi]
            repository: https://upload.pypi.org/legacy/
            username:username
            password:password
        """))
    s = settings.Settings(config_file=pypirc)
    assert (s.repository_config['repository'] ==
            'https://upload.pypi.org/legacy/')
    assert s.sign is False
    assert s.sign_with == 'gpg'
    assert s.identity is None
    assert s.username == 'username'
    assert s.password == 'password'
    assert s.cacert is None
    assert s.client_cert is None
    assert s.disable_progress_bar is False


def test_identity_requires_sign():
    """Verify that if a user passes identity, we require sign=True."""
    with pytest.raises(exceptions.InvalidSigningConfiguration):
        settings.Settings(sign=False, identity='fakeid')
