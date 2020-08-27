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
import logging
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


@pytest.mark.parametrize(
    "verbose, log_level", [(True, logging.INFO), (False, logging.WARNING)]
)
def test_setup_logging(verbose, log_level):
    """Set log level based on verbose field."""
    settings.Settings(verbose=verbose)

    logger = logging.getLogger("twine")

    assert logger.level == log_level


@pytest.mark.parametrize(
    "verbose",
    [True, False],
)
def test_print_config_path_if_verbose(tmpdir, capsys, make_settings, verbose):
    """Print the location of the .pypirc config used by the user."""
    pypirc = os.path.join(str(tmpdir), ".pypirc")

    make_settings(verbose=verbose)

    captured = capsys.readouterr()

    if verbose:
        assert captured.out == f"Using configuration from {pypirc}\n"
    else:
        assert captured.out == ""


def test_identity_requires_sign():
    """Raise an exception when user provides identity but doesn't require sigining."""
    with pytest.raises(exceptions.InvalidSigningConfiguration):
        settings.Settings(sign=False, identity="fakeid")


@pytest.mark.parametrize("client_cert", [None, ""])
def test_password_is_required_if_no_client_cert(client_cert, entered_password):
    """Set password when client_cert is not provided."""
    settings_obj = settings.Settings(username="fakeuser", client_cert=client_cert)
    assert settings_obj.password == "entered pw"


def test_client_cert_and_password_both_set_if_given():
    """Set password and client_cert when both are provided."""
    client_cert = "/random/path"
    settings_obj = settings.Settings(
        username="fakeuser", password="anything", client_cert=client_cert
    )
    assert settings_obj.password == "anything"
    assert settings_obj.client_cert == client_cert


def test_password_required_if_no_client_cert_and_non_interactive():
    """Raise exception if no password or client_cert when non interactive."""
    settings_obj = settings.Settings(username="fakeuser", non_interactive=True)
    with pytest.raises(exceptions.NonInteractive):
        settings_obj.password


def test_no_password_prompt_if_client_cert_and_non_interactive(entered_password):
    """Don't prompt for password when client_cert is provided and non interactive."""
    client_cert = "/random/path"
    settings_obj = settings.Settings(
        username="fakeuser", client_cert=client_cert, non_interactive=True
    )
    assert not settings_obj.password


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
