# Copyright 2016 Donald Stufft
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

import functools

from twine.cli import twine as _twine

# We need to import our twine.commands package so that all of our commands get
# registered.
# Note: We import this as _ so that we don't expose the imported name.
import twine.commands as _  # noqa


twine = functools.partial(_twine, auto_envvar_prefix="TWINE")


__all__ = ["twine"]
