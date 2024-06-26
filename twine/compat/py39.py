import sys

if sys.version_info >= (3, 10):
    import importlib.metadata

    deps = ()
else:

    class importlib:
        import importlib_metadata as metadata  # noqa: F401

    deps = ("importlib_metadata",)


__all__ = ["importlib", "deps"]
