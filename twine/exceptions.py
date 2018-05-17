"""Module containing exceptions raised by twine."""
# Copyright 2015 Ian Stapleton Cordasco
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


class TwineException(Exception):
    """Base class for all exceptions raised by twine."""

    pass


class RedirectDetected(TwineException):
    """A redirect was detected that the user needs to resolve.

    In some cases, requests refuses to issue a new POST request after a
    redirect. In order to prevent a confusing user experience, we raise this
    exception to allow users to know the index they're uploading to is
    redirecting them.
    """

    pass


class PackageNotFound(TwineException):
    """A package file was provided that could not be found on the file system.

    This is only used when attempting to register a package.
    """

    pass


class UploadToDeprecatedPyPIDetected(TwineException):
    """An upload attempt was detected to deprecated PyPI domains.

    The sites pypi.python.org and testpypi.python.org are deprecated.
    """

    pass


class UnreachableRepositoryURLDetected(TwineException):
    """An upload attempt was detected to a URL without a protocol prefix.

    All repository URLs must have a protocol (e.g., ``https://``).
    """

    pass


class InvalidSigningConfiguration(TwineException):
    """Both the sign and identity parameters must be present."""

    pass
