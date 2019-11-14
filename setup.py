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
from setuptools import setup


setup(
    name="twine",
    version="2.0.0",

    description="Collection of utilities for publishing packages on PyPI",
    long_description=open("README.rst").read(),
    url="https://twine.readthedocs.io/",
    project_urls={
        'Packaging tutorial': 'https://packaging.python.org/tutorials/distributing-packages/',
        'Travis CI': 'https://travis-ci.org/pypa/twine',
        'Twine documentation': 'https://twine.readthedocs.io/en/latest/',
        'Twine source': 'https://github.com/pypa/twine/',
    },

    author="Donald Stufft and individual contributors",
    author_email="donald@stufft.io",

    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],

    packages=["twine", "twine.commands"],

    entry_points={
        "twine.registered_commands": [
            "check = twine.commands.check:main",
            "upload = twine.commands.upload:main",
            "register = twine.commands.register:main",
        ],
        "console_scripts": [
            "twine = twine.__main__:main",
        ],
    },

    python_requires=">=3.6",
    install_requires=[
        "pkginfo >= 1.4.2",
        "readme_renderer >= 21.0",
        "requests >= 2.20",
        "requests-toolbelt >= 0.8.0, != 0.9.0",
        "setuptools >= 0.7.0",
        "tqdm >= 4.14",
        'importlib_metadata; python_version<"3.8"',
        "keyring >= 15.1",
    ],
    setup_requires=[
        'setuptools_scm>=1.15',
    ],
)
