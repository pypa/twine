"""Test functions useful across twine's tests."""

import contextlib
import os


@contextlib.contextmanager
def set_env(**environ):
    """Set the process environment variables temporarily.

    >>> with set_env(PLUGINS_DIR=u'test/plugins'):
    ...   "PLUGINS_DIR" in os.environ
    True

    >>> "PLUGINS_DIR" in os.environ
    False

    :param environ: Environment variables to set
    :type environ: dict[str, unicode]
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)
