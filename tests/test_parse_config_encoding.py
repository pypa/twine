import builtins
import logging
import pathlib

from twine import utils


def _write_utf8_ini(path, username: str = "テストユーザー🐍") -> None:
    """
    Helper that writes an ini file encoded in UTF-8.
    Including an emoji makes decoding more likely to fail under locales like cp932.
    """
    content = f"""[server-login]
username = {username}
password = secret
"""
    # Write explicitly as UTF-8 bytes (so reading will fail if the reader assumes a different encoding)
    path.write_bytes(content.encode("utf-8"))


def test_parse_config_triggers_utf8_fallback(monkeypatch, caplog, tmp_path):
    """
    If the first read of the file raises a UnicodeDecodeError, _parse_config
    should take the UTF-8 fallback path. This test simulates a decode failure
    on the first I/O and then allows normal I/O so the fallback is exercised.
    """
    ini_path = tmp_path / "pypirc"
    expected_username = "テストユーザー🐍"
    _write_utf8_ini(ini_path, expected_username)

    # Coordinate a single "raise once" behavior across multiple common I/O entrypoints.
    call = {"n": 0}
    original_open = builtins.open
    original_read_text = pathlib.Path.read_text

    def open_raise_once(*args, **kwargs):
        # Only raise on the very first attempted open; afterwards delegate to real open.
        if call["n"] == 0:
            call["n"] += 1
            # UnicodeDecodeError(encoding, object, start, end, reason)
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "simulated")
        return original_open(*args, **kwargs)

    def read_text_raise_once(self, encoding=None, errors=None):
        # Only raise on the very first attempted read_text; afterwards delegate.
        if call["n"] == 0:
            call["n"] += 1
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "simulated")
        return original_read_text(self, encoding=encoding, errors=errors)

    # Patch both builtins.open and pathlib.Path.read_text to be robust against
    # whichever API _parse_config uses internally.
    monkeypatch.setattr(builtins, "open", open_raise_once)
    monkeypatch.setattr(pathlib.Path, "read_text", read_text_raise_once, raising=True)

    caplog.set_level(logging.INFO, logger="twine")
    parser = utils._parse_config(str(ini_path))

    # Ensure the parsed result is correct (file was read as UTF-8 after fallback)
    assert parser.get("server-login", "username") == expected_username

    # Ensure a log message indicating the fallback is present
    assert (
        "Configuration file not readable with default locale encoding, trying UTF-8"
        in caplog.text
    )


def test_parse_config_no_fallback_when_default_utf8(monkeypatch, caplog, tmp_path):
    """
    When the default encoding is UTF-8, no fallback is necessary and the file
    should be parsed via the normal path. To make this deterministic across
    Python versions/environments, force I/O calls without an explicit encoding
    to use UTF-8 by wrapping open / Path.read_text.
    """
    ini_path = tmp_path / "pypirc"
    expected_username = "テストユーザー🐍"
    _write_utf8_ini(ini_path, expected_username)

    # Wrap builtins.open so that if encoding is not provided, we force utf-8.
    original_open = builtins.open

    def open_force_utf8(
        file,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None,
    ):
        if encoding is None and "b" not in mode:
            # delegate to real open but force utf-8 as default encoding
            return original_open(
                file,
                mode,
                buffering=buffering,
                encoding="utf-8",
                errors=errors,
                newline=newline,
                closefd=closefd,
                opener=opener,
            )
        return original_open(
            file,
            mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            closefd=closefd,
            opener=opener,
        )

    # Wrap pathlib.Path.read_text similarly
    original_read_text = pathlib.Path.read_text

    def read_text_force_utf8(self, encoding=None, errors=None):
        if encoding is None:
            return original_read_text(self, encoding="utf-8", errors=errors)
        return original_read_text(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(builtins, "open", open_force_utf8)
    monkeypatch.setattr(pathlib.Path, "read_text", read_text_force_utf8, raising=True)

    caplog.set_level(logging.INFO, logger="twine")
    parser = utils._parse_config(str(ini_path))

    # Ensure the parsed result is correct
    assert parser.get("server-login", "username") == expected_username

    # Verify that the used configuration file path is present in the logs.
    assert f"Parsing configuration from {ini_path}" in caplog.text
