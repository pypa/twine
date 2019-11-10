import pretend
import pytest

from twine import cli
import twine.commands.upload


def test_dispatch_to_subcommand(monkeypatch):
    replaced_main = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(twine.commands.upload, "main", replaced_main)

    cli.dispatch(["upload", "path/to/file"])

    assert replaced_main.calls == [pretend.call(["path/to/file"])]


def test_catches_enoent():
    with pytest.raises(SystemExit):
        cli.dispatch(["non-existent-command"])
