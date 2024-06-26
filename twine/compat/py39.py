import sys

if sys.version_info >= (3, 10):
    import importlib.metadata
else:

    class importlib:
        import importlib_metadata as metadata  # noqa: F401


__all__ = ['importlib']
