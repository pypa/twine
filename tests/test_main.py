from twine import __main__ as dunder_main
from twine import exceptions

import pretend


def test_exception_handling(monkeypatch):
    replaced_dispatch = pretend.raiser(
        exceptions.InvalidConfiguration('foo')
    )
    monkeypatch.setattr(dunder_main, 'dispatch', replaced_dispatch)
    assert dunder_main.main() == 'InvalidConfiguration: foo'
