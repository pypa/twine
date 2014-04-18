
import pytest

from twine.commands import upload


@pytest.mark.parametrize(
    ('cli_value', 'config', 'key', 'strategy', 'expected'),
    (
        ('cli', {}, 'key', lambda: 'fallback', 'cli'),
        (None, {'key': 'value'}, 'key', lambda: 'fallback', 'value'),
        (None, {}, 'key', lambda: 'fallback', 'fallback'),
    ),
)
def test_get_userpass_value(cli_value, config, key, strategy, expected):
    ret = upload.get_userpass_value(cli_value, config, key, strategy)
    assert ret == expected
