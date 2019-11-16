import warnings
import getpass
import functools

import keyring
import munch

from . import utils
from . import exceptions


class Resolver:
    def __init__(self, settings, username=None, password=None):
        self.settings = settings
        self.input = munch.Munch(username=username, password=password)

    @property
    @functools.lru_cache()
    def username(self):
        return utils.get_userpass_value(
            self.input.username,
            self.config,
            key='username',
            prompt_strategy=self.username_from_keyring_or_prompt,
        )

    @property
    @functools.lru_cache()
    def password(self):
        return utils.get_userpass_value(
            self.input.password,
            self.config,
            key='password',
            prompt_strategy=self.password_from_keyring_or_prompt,
        )

    @property
    def system(self):
        return self.settings.system

    @property
    def config(self):
        return self.settings.repository_config

    def get_username_from_keyring(self):
        try:
            creds = keyring.get_credential(self.system, None)
            if creds:
                return creds.username
        except AttributeError:
            # To support keyring prior to 15.2
            pass
        except Exception as exc:
            warnings.warn(str(exc))

    def get_password_from_keyring(self):
        try:
            return keyring.get_password(self.system, self.username)
        except Exception as exc:
            warnings.warn(str(exc))

    def username_from_keyring_or_prompt(self):
        return (
            self.get_username_from_keyring()
            or self.prompt('username', input)
        )

    def password_from_keyring_or_prompt(self):
        return (
            self.get_password_from_keyring()
            or self.prompt('password', getpass.getpass)
        )

    def prompt(self, what, how=None):
        return how(f"Enter your {what}: ")


class Private(Resolver):
    def prompt(self, what, how=None):
        raise exceptions.NonInteractive(f"Credential not found for {what}.")
