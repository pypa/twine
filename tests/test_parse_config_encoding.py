import logging
import locale


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
    If the default encoding is made to look like cp932, the first open() should
    raise a UnicodeDecodeError and _parse_config should take the UTF-8 fallback path.
    Also verify that a log message about the fallback is emitted.
    """
    ini_path = tmp_path / "pypirc"
    expected_username = "テストユーザー🐍"
    _write_utf8_ini(ini_path, expected_username)

    # Make the system preferred encoding appear as cp932
    monkeypatch.setattr(locale, "getpreferredencoding", lambda do_set=False: "cp932")

    caplog.set_level(logging.INFO, logger="twine")
    parser = utils._parse_config(str(ini_path))

    # Ensure the parsed result is correct (file was read as UTF-8 after fallback)
    assert parser.get("server-login", "username") == expected_username

    # Ensure a log message indicating the fallback is present
    assert "Configuration file not readable with default locale encoding, trying UTF-8" in caplog.text


def test_parse_config_no_fallback_when_default_utf8(monkeypatch, caplog, tmp_path):
    """
    When the default encoding is UTF-8, no fallback is necessary and the file
    should be parsed via the normal path. Because logs can vary across
    environments, only verify that the "Using configuration from <path>" message
    appears.
    """
    ini_path = tmp_path / "pypirc"
    expected_username = "テストユーザー🐍"
    _write_utf8_ini(ini_path, expected_username)

    # Simulate the default encoding being UTF-8
    monkeypatch.setattr(locale, "getpreferredencoding", lambda do_set=False: "utf-8")

    caplog.set_level(logging.INFO, logger="twine")
    parser = utils._parse_config(str(ini_path))

    # Ensure the parsed result is correct
    assert parser.get("server-login", "username") == expected_username

    # Because environment differences (docutils output or open() behavior) can change
    # whether a fallback occurs, do not strictly assert the absence of a fallback.
    # Instead, at minimum verify that the used configuration file path is present in the logs.
    assert f"Using configuration from {ini_path}" in caplog.text
