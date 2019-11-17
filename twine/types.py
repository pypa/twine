import typing


class CredentialInput(typing.NamedTuple):
    username: typing.Optional[str]
    password: typing.Optional[str]

    @classmethod
    def new(cls, username=None, password=None):
        return cls(username, password)
