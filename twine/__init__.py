# Copyright 2018 Donald Stufft and individual contributors
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
__all__ = (
    "__title__", "__summary__", "__uri__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
)

__copyright__ = "Copyright 2019 Donald Stufft and individual contributors"


try:
    # https://github.com/python/mypy/issues/1393
    from importlib.metadata import metadata  # type: ignore
except ImportError:
    # https://github.com/python/mypy/issues/1153
    from importlib_metadata import metadata  # type: ignore


twine_metadata = metadata('twine')


__title__ = twine_metadata['name']
__summary__ = twine_metadata['summary']
__uri__ = twine_metadata['home-page']
__version__ = twine_metadata['version']
__author__ = twine_metadata['author']
__email__ = twine_metadata['author-email']
__license__ = twine_metadata['license']
