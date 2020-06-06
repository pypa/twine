"""Tests for the Settings class and module."""
# Copyright 2018 Ian Stapleton Cordasco
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
import argparse
import os.path
import textwrap

import pytest

from twine import exceptions
from twine import settings


def test_settings_takes_no_positional_arguments():
    """Raise an exception when Settings is initialized without keyword arguments."""
    with pytest.raises(TypeError):
        settings.Settings("a", "b", "c")


def test_settings_transforms_repository_config(tmpdir):
    """Set repository config and defaults when .pypirc is provided."""
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    with open(pypirc, "w") as fp:
        fp.write(
            textwrap.dedent(
                """
            [pypi]
            repository: https://upload.pypi.org/legacy/
            username:username
            password:password
        """
            )
        )
    s = settings.Settings(config_file=pypirc)
    assert s.repository_config["repository"] == "https://upload.pypi.org/legacy/"
    assert s.sign is False
    assert s.sign_with == "gpg"
    assert s.identity is None
    assert s.username == "username"
    assert s.password == "password"
    assert s.cacert is None
    assert s.client_cert is None
    assert s.disable_progress_bar is False


def test_identity_requires_sign():
    """Raise an exception when user provides identity but doesn't require sigining."""
    with pytest.raises(exceptions.InvalidSigningConfiguration):
        settings.Settings(sign=False, identity="fakeid")


def test_password_not_required_if_client_cert(entered_password):
    """Don't set password when only client_cert is provided."""
    test_client_cert = "/random/path"
    settings_obj = settings.Settings(username="fakeuser", client_cert=test_client_cert)
    assert not settings_obj.password
    assert settings_obj.client_cert == test_client_cert


@pytest.mark.parametrize("client_cert", [None, ""])
def test_password_is_required_if_no_client_cert(client_cert, entered_password):
    """Set password when client_cert is not provided."""
    settings_obj = settings.Settings(username="fakeuser", client_cert=client_cert)
    assert settings_obj.password == "entered pw"


def test_client_cert_is_set_and_password_not_if_both_given(entered_password):
    """Set password and client_cert when both are provided."""
    client_cert = "/random/path"
    settings_obj = settings.Settings(
        username="fakeuser", password="anything", client_cert=client_cert
    )
    assert not settings_obj.password
    assert settings_obj.client_cert == client_cert


class TestArgumentParsing:
    @staticmethod
    def parse_args(args):
        parser = argparse.ArgumentParser()
        settings.Settings.register_argparse_arguments(parser)
        return parser.parse_args(args)

    def test_non_interactive_flag(self):
        args = self.parse_args(["--non-interactive"])
        assert args.non_interactive

    def test_non_interactive_environment(self, monkeypatch):
        monkeypatch.setenv("TWINE_NON_INTERACTIVE", "1")
        args = self.parse_args([])
        assert args.non_interactive
        monkeypatch.setenv("TWINE_NON_INTERACTIVE", "0")
        args = self.parse_args([])
        assert not args.non_interactive
