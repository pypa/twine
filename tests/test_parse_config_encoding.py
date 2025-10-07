import logging
import locale

import pytest

from twine import utils

def _write_utf8_ini(path, username: str = "テストユーザー🐍") -> None:
    """
    UTF-8 で ini ファイルを書き出すヘルパー。
    絵文字を含めることで cp932 などのロケールではデコードに失敗しやすくします。
    """
    content = f"""[server-login]
username = {username}
password = secret
"""
    # 明示的に UTF-8 バイト列で書く（読み取り側が別エンコーディングを想定した場合に失敗させるため）
    path.write_bytes(content.encode("utf-8"))

def test_parse_config_triggers_utf8_fallback(monkeypatch, caplog, tmp_path):
    """
    デフォルトエンコーディングを cp932 に見せかけると最初の open() が
    UnicodeDecodeError を出し、_parse_config が UTF-8 フォールバック経路を通ることを確認する。
    また、ログにフォールバック通知が出ていることも検証する。
    """
    ini_path = tmp_path / "pypirc"
    expected_username = "テストユーザー🐍"
    _write_utf8_ini(ini_path, expected_username)

    # システム既定のエンコーディングが cp932 のように見せかける
    monkeypatch.setattr(locale, "getpreferredencoding", lambda do_set=False: "cp932")

    caplog.set_level(logging.INFO)
    parser = utils._parse_config(str(ini_path))

    # パース結果が正しいこと（フォールバック後に UTF-8 として読めている）
    assert parser.get("server-login", "username") == expected_username

    # フォールバックしたことを示すログメッセージが出ていること
    assert "decoded with UTF-8 fallback" in caplog.text

def test_parse_config_no_fallback_when_default_utf8(monkeypatch, caplog, tmp_path):
    """
    デフォルトエンコーディングが UTF-8 の場合、フォールバックは不要で
    通常経路でパースされ、フォールバックのログが出ないことを確認する。
    """
    ini_path = tmp_path / "pypirc"
    expected_username = "テストユーザー🐍"
    _write_utf8_ini(ini_path, expected_username)

    # デフォルトエンコーディングが UTF-8 の場合
    monkeypatch.setattr(locale, "getpreferredencoding", lambda do_set=False: "utf-8")

    caplog.set_level(logging.INFO)
    parser = utils._parse_config(str(ini_path))

    # パース結果が正しいこと
    assert parser.get("server-login", "username") == expected_username

    # フォールバック通知が出ていないこと（通常の使用メッセージは出るはず）
    assert "decoded with UTF-8 fallback" not in caplog.text
    assert f"Using configuration from {ini_path}" in caplog.text
