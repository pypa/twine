# Copyright 2018 Dustin Ingram
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import io

import pretend
import pytest

from twine import commands
from twine import package as package_file
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

        assert self.stream.output.write.calls == [pretend.call("this does not match")]

    def test_str_representation(self):
        assert str(self.stream) == "result"


class TestCheckLicense:
    def test_license_field_specified(self, monkeypatch):
        package = pretend.stub(
            metadata_dictionary=lambda: {
                "license": "Some License v42.0",
            }
        )

        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )

        warnings, errors = check.check_license("dist/dist.tar.gz")
        assert not warnings
        assert not errors

    def test_license_classifier_specified(self, monkeypatch):
        package = pretend.stub(
            metadata_dictionary=lambda: {
                "classifiers": [
                    "License :: OSI Approved :: Apache Software License",
                ],
            }
        )

        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )

        warnings, errors = check.check_license("dist/dist.tar.gz")
        assert not warnings
        assert not errors

    def test_no_license_specified(self, monkeypatch):
        package = pretend.stub(metadata_dictionary=lambda: {})

        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )

        warnings, errors = check.check_license("dist/dist.tar.gz")
        assert not errors
        assert warnings == [
            "No license specified. Use one of the `LICENSE ::` classifiers "
            "or the `license` field if no classifier is relevant."
        ]


class TestCheckLongDescription:
    def test_passing_distribution(self, monkeypatch):
        renderer = pretend.stub(render=pretend.call_recorder(lambda *a, **kw: "valid"))
        package = pretend.stub(
            metadata_dictionary=lambda: {
                "description": "blah",
                "description_content_type": "text/markdown",
            }
        )

        warning_stream = ""

        monkeypatch.setattr(check, "_RENDERERS", {None: renderer})
        monkeypatch.setattr(commands, "_find_dists", lambda a: ["dist/dist.tar.gz"])
        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )
        monkeypatch.setattr(check, "_WarningStream", lambda: warning_stream)

        warnings, errors = check.check_long_description("dist/dist.tar.gz")
        assert not warnings
        assert not errors
        assert renderer.render.calls == [pretend.call("blah", stream=warning_stream)]

    @pytest.mark.parametrize("content_type", ["text/plain", "text/markdown"])
    def test_passing_distribution_with_none_renderer(
        self, content_type, monkeypatch
    ):
        """Pass when rendering a content type can't fail."""
        package = pretend.stub(
            metadata_dictionary=lambda: {
                "description": "blah",
                "description_content_type": content_type,
            }
        )

        monkeypatch.setattr(commands, "_find_dists", lambda a: ["dist/dist.tar.gz"])
        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )

        warnings, errors = check.check_long_description("dist/dist.tar.gz")
        assert not warnings
        assert not errors

    def test_no_description(self, monkeypatch, capsys):
        package = pretend.stub(
            metadata_dictionary=lambda: {
                "description": None,
                "description_content_type": None,
            }
        )

        monkeypatch.setattr(commands, "_find_dists", lambda a: ["dist/dist.tar.gz"])
        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )

        # used to crash with `AttributeError`
        output_stream = io.StringIO()
        assert not check.check(["dist/*"], output_stream=output_stream)
        warnings, errors = check.check_long_description("dist/dist.tar.gz")
        assert not errors
        assert warnings == [
            "`long_description_content_type` missing. defaulting to `text/x-rst`.",
            "`long_description` missing.",
        ]

    def test_rendering_failure(self, monkeypatch):
        renderer = pretend.stub(render=pretend.call_recorder(lambda *a, **kw: None))
        package = pretend.stub(
            metadata_dictionary=lambda: {
                "description": "blah",
                "description_content_type": "text/markdown",
            }
        )
        warning_stream = "WARNING"

        monkeypatch.setattr(check, "_RENDERERS", {None: renderer})
        monkeypatch.setattr(commands, "_find_dists", lambda a: ["dist/dist.tar.gz"])
        monkeypatch.setattr(
            package_file,
            "PackageFile",
            pretend.stub(from_filename=lambda *a, **kw: package),
        )
        monkeypatch.setattr(check, "_WarningStream", lambda: warning_stream)
        warnings, errors = check.check_long_description("dist/dist.tar.gz")
        assert not warnings
        assert errors == [
            "  `long_description` has syntax errors in markup and "
            "would not be rendered on PyPI.",
            "    WARNING",
        ]


class TestCheckCommand:
    def test_strict_fails_on_warnings(self, monkeypatch):
        monkeypatch.setattr(commands, "_find_dists", lambda a: ["dist/dist.tar.gz"])
        monkeypatch.setattr(check, "_check_file", lambda *args: (["warning"], []))
        assert not check.check(["dist/dist.tar.gz"], strict=False)
        assert check.check(["dist/dist.tar.gz"], strict=True)

    def test_check_no_distributions(self, monkeypatch):
        stream = io.StringIO()

        monkeypatch.setattr(commands, "_find_dists", lambda a: [])

        assert not check.check(["dist/*"], output_stream=stream)
        assert stream.getvalue() == "No files to check.\n"

    def test_main(self, monkeypatch):
        check_result = pretend.stub()
        check_stub = pretend.call_recorder(lambda a, strict=False: check_result)
        monkeypatch.setattr(check, "check", check_stub)

        assert check.main(["dist/*"]) == check_result
        assert check_stub.calls == [pretend.call(["dist/*"], strict=False)]
