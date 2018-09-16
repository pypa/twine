# Copyright 2018 Dustin Ingram
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import unicode_literals

import pretend

from twine.commands import check


def test_warningstream_write_match():
    stream = check._WarningStream()
    stream.output = pretend.stub(write=pretend.call_recorder(lambda a: None))

    stream.write("<string>:2: (WARNING/2) Title underline too short.")

    assert stream.output.write.calls == [
        pretend.call("line 2: Warning: Title underline too short.\n")
    ]


def test_warningstream_write_nomatch():
    stream = check._WarningStream()
    stream.output = pretend.stub(write=pretend.call_recorder(lambda a: None))

    stream.write("this does not match")

    assert stream.output.write.calls == [pretend.call("this does not match")]


def test_warningstream_str():
    stream = check._WarningStream()
    stream.output = pretend.stub(getvalue=lambda: "result")

    assert str(stream) == "result"


def test_check_no_distributions(monkeypatch):
    stream = check.StringIO()

    monkeypatch.setattr(check, "_find_dists", lambda a: [])

    assert not check.check("dist/*", output_stream=stream)
    assert stream.getvalue() == ""


def test_check_passing_distribution(monkeypatch):
    renderer = pretend.stub(
        render=pretend.call_recorder(lambda *a, **kw: "valid")
    )
    package = pretend.stub(metadata_dictionary=lambda: {"description": "blah"})
    output_stream = check.StringIO()
    warning_stream = ""

    monkeypatch.setattr(check, "_RENDERERS", {"": renderer})
    monkeypatch.setattr(check, "_find_dists", lambda a: ["dist/dist.tar.gz"])
    monkeypatch.setattr(
        check,
        "PackageFile",
        pretend.stub(from_filename=lambda *a, **kw: package),
    )
    monkeypatch.setattr(check, "_WarningStream", lambda: warning_stream)

    assert not check.check("dist/*", output_stream=output_stream)
    assert (
        output_stream.getvalue()
        == "Checking distribution dist/dist.tar.gz: Passed\n"
    )
    assert renderer.render.calls == [
        pretend.call("blah", stream=warning_stream)
    ]


def test_check_failing_distribution(monkeypatch):
    renderer = pretend.stub(
        render=pretend.call_recorder(lambda *a, **kw: None)
    )
    package = pretend.stub(metadata_dictionary=lambda: {"description": "blah"})
    output_stream = check.StringIO()
    warning_stream = "WARNING"

    monkeypatch.setattr(check, "_RENDERERS", {"": renderer})
    monkeypatch.setattr(check, "_find_dists", lambda a: ["dist/dist.tar.gz"])
    monkeypatch.setattr(
        check,
        "PackageFile",
        pretend.stub(from_filename=lambda *a, **kw: package),
    )
    monkeypatch.setattr(check, "_WarningStream", lambda: warning_stream)

    assert check.check("dist/*", output_stream=output_stream)
    assert output_stream.getvalue() == (
        "Checking distribution dist/dist.tar.gz: Failed\n"
        "The project's long_description has invalid markup which will not be "
        "rendered on PyPI. The following syntax errors were detected:\n"
        "WARNING"
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
