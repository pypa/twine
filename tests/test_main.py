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

import pretend

from twine import __main__ as dunder_main
from twine import exceptions


def test_exception_handling(monkeypatch):
    replaced_dispatch = pretend.raiser(exceptions.InvalidConfiguration("foo"))
    monkeypatch.setattr(dunder_main, "dispatch", replaced_dispatch)
    assert dunder_main.main() == "InvalidConfiguration: foo"
