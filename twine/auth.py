import functools
import getpass
import logging
from typing import TYPE_CHECKING, Callable, Optional, Type, cast
from urllib.parse import urlparse

import requests
from id import detect_credential  # type: ignore

# keyring has an indirect dependency on PyCA cryptography, which has no
# pre-built wheels for ppc64le and s390x, see #1158.
if TYPE_CHECKING:
    import keyring
else:
    try:
        import keyring
    except ModuleNotFoundError:  # pragma: no cover
        keyring = None

from twine import exceptions
from twine import utils

logger = logging.getLogger(__name__)


class CredentialInput:
    def __init__(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        self.username = username
        self.password = password


class Resolver:
    def __init__(
        self,
        config: utils.RepositoryConfig,
        input: CredentialInput,
    ) -> None:
        self.config = config
        self.input = input

    @classmethod
    def choose(cls, interactive: bool) -> Type["Resolver"]:
        return cls if interactive else Private

    @property
    @functools.lru_cache()
    def username(self) -> Optional[str]:
        if self.is_pypi() and not self.input.username:
            # Default username.
            self.input.username = "__token__"

        return utils.get_userpass_value(
            self.input.username,
            self.config,
            key="username",
            prompt_strategy=self.username_from_keyring_or_prompt,
        )

    @property
    @functools.lru_cache()
    def password(self) -> Optional[str]:
        if (
            self.is_pypi()
            and self.username == "__token__"
            and self.input.password is None
        ):
            logger.info(
                "Trying to use trusted publishing (no token was explicitly provided)"
            )
            return self.make_trusted_publishing_token()

        return utils.get_userpass_value(
            self.input.password,
            self.config,
            key="password",
            prompt_strategy=self.password_from_keyring_or_prompt,
        )

    def make_trusted_publishing_token(self) -> str:
        # Trusted publishing (OpenID Connect): get one token from the CI
        # system, and exchange that for a PyPI token.
        repository_domain = cast(str, urlparse(self.system).netloc)
        session = requests.Session()  # TODO: user agent & retries

        # Indices are expected to support `https://{domain}/_/oidc/audience`,
        # which tells OIDC exchange clients which audience to use.
        audience_url = f"https://{repository_domain}/_/oidc/audience"
        resp = session.get(audience_url, timeout=5)
        resp.raise_for_status()
        audience = cast(str, resp.json()["audience"])

        oidc_token = detect_credential(audience)
        logger.debug("Got OIDC token for audience %s", audience)

        token_exchange_url = f"https://{repository_domain}/_/oidc/mint-token"

        mint_token_resp = session.post(
            token_exchange_url,
            json={"token": oidc_token},
            timeout=5,  # S113 wants a timeout
        )
        mint_token_resp.raise_for_status()
        logger.debug("Minted upload token for trusted publishing")
        return cast(str, mint_token_resp.json()["token"])

    @property
    def system(self) -> Optional[str]:
        return self.config["repository"]

    def get_username_from_keyring(self) -> Optional[str]:
        if keyring is None:
            logger.info("keyring module is not available")
            return None
        try:
            system = cast(str, self.system)
            logger.info("Querying keyring for username")
            creds = keyring.get_credential(system, None)
            if creds:
                return creds.username
        except AttributeError:
            # To support keyring prior to 15.2
            pass
        except Exception as exc:
            logger.warning("Error getting username from keyring", exc_info=exc)
        return None

    def get_password_from_keyring(self) -> Optional[str]:
        if keyring is None:
            logger.info("keyring module is not available")
            return None
        try:
            system = cast(str, self.system)
            username = cast(str, self.username)
            logger.info("Querying keyring for password")
            return cast(str, keyring.get_password(system, username))
        except Exception as exc:
            logger.warning("Error getting password from keyring", exc_info=exc)
        return None

    def username_from_keyring_or_prompt(self) -> str:
        username = self.get_username_from_keyring()
        if username:
            logger.info("username set from keyring")
            return username

        return self.prompt("username", input)

    def password_from_keyring_or_prompt(self) -> str:
        password = self.get_password_from_keyring()
        if password:
            logger.info("password set from keyring")
            return password

        # Prompt for API token when required.
        what = "API token" if self.is_pypi() else "password"

        return self.prompt(what, getpass.getpass)

    def prompt(self, what: str, how: Callable[..., str]) -> str:
        return how(f"Enter your {what}: ")

    def is_pypi(self) -> bool:
        """As of 2024-01-01, PyPI requires API tokens for uploads."""
        return cast(str, self.config["repository"]).startswith(
            (
                utils.DEFAULT_REPOSITORY,
                utils.TEST_REPOSITORY,
            )
        )


class Private(Resolver):
    def prompt(self, what: str, how: Optional[Callable[..., str]] = None) -> str:
        raise exceptions.NonInteractive(f"Credential not found for {what}.")
