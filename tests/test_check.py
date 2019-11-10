import pretend

from twine.commands import check


class TestWarningStream:

    def setup(self):
        self.stream = check._WarningStream()
        self.stream.output = pretend.stub(
            write=pretend.call_recorder(lambda a: None),
            getvalue=lambda: "result",
        )

    def test_write_match(self):
        self.stream.write("<string>:2: (WARNING/2) Title underline too short.")

        assert self.stream.output.write.calls == [
            pretend.call("line 2: Warning: Title underline too short.\n")
        ]

    def test_write_nomatch(self):
        self.stream.write("this does not match")

        assert self.stream.output.write.calls == [
            pretend.call("this does not match")
        ]

    def test_str_representation(self):
        assert str(self.stream) == "result"


def test_check_no_distributions(monkeypatch):
    stream = check.StringIO()

    monkeypatch.setattr(check, "_find_dists", lambda a: [])

    assert not check.check("dist/*", output_stream=stream)
    assert stream.getvalue() == "No files to check.\n"


def test_check_passing_distribution(monkeypatch):
    renderer = pretend.stub(
        render=pretend.call_recorder(lambda *a, **kw: "valid")
    )
    package = pretend.stub(metadata_dictionary=lambda: {
        "description": "blah", 'description_content_type': 'text/markdown',
    })
    output_stream = check.StringIO()
    warning_stream = ""

    monkeypatch.setattr(check, "_RENDERERS", {None: renderer})
    monkeypatch.setattr(check, "_find_dists", lambda a: ["dist/dist.tar.gz"])
    monkeypatch.setattr(
        check,
        "PackageFile",
        pretend.stub(from_filename=lambda *a, **kw: package),
    )
    monkeypatch.setattr(check, "_WarningStream", lambda: warning_stream)

    assert not check.check("dist/*", output_stream=output_stream)
    assert output_stream.getvalue() == "Checking dist/dist.tar.gz: PASSED\n"
    assert renderer.render.calls == [
        pretend.call("blah", stream=warning_stream)
    ]


def test_check_no_description(monkeypatch, capsys):
    package = pretend.stub(metadata_dictionary=lambda: {
        'description': None, 'description_content_type': None,
    })

    monkeypatch.setattr(check, "_find_dists", lambda a: ["dist/dist.tar.gz"])
    monkeypatch.setattr(
        check,
        "PackageFile",
        pretend.stub(from_filename=lambda *a, **kw: package),
    )

    # used to crash with `AttributeError`
    output_stream = check.StringIO()
    check.check("dist/*", output_stream=output_stream)
    assert output_stream.getvalue() == (
        'Checking dist/dist.tar.gz: PASSED, with warnings\n'
        '  warning: `long_description_content_type` missing.  '
        'defaulting to `text/x-rst`.\n'
        '  warning: `long_description` missing.\n'
    )


def test_check_failing_distribution(monkeypatch):
    renderer = pretend.stub(
        render=pretend.call_recorder(lambda *a, **kw: None)
    )
    package = pretend.stub(metadata_dictionary=lambda: {
        "description": "blah", "description_content_type": 'text/markdown',
    })
    output_stream = check.StringIO()
    warning_stream = "WARNING"

    monkeypatch.setattr(check, "_RENDERERS", {None: renderer})
    monkeypatch.setattr(check, "_find_dists", lambda a: ["dist/dist.tar.gz"])
    monkeypatch.setattr(
        check,
        "PackageFile",
        pretend.stub(from_filename=lambda *a, **kw: package),
    )
    monkeypatch.setattr(check, "_WarningStream", lambda: warning_stream)

    assert check.check("dist/*", output_stream=output_stream)
    assert output_stream.getvalue() == (
        "Checking dist/dist.tar.gz: FAILED\n"
        "  `long_description` has syntax errors in markup and would not be "
        "rendered on PyPI.\n"
        "    WARNING"
    )
    assert renderer.render.calls == [
        pretend.call("blah", stream=warning_stream)
    ]


def test_main(monkeypatch):
    check_result = pretend.stub()
    check_stub = pretend.call_recorder(lambda a: check_result)
    monkeypatch.setattr(check, "check", check_stub)

    assert check.main(["dist/*"]) == check_result
    assert check_stub.calls == [pretend.call(["dist/*"])]
