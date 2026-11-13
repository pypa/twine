Improve the error message shown when GitHub Actions refuses to issue an OIDC
token for trusted publishing.

The message now recommends the ``id-token: write`` permission explicitly, and
notes that pull requests from forks are never granted OIDC permissions even
when that permission is configured.
