# Copyright 2013 Donald Stufft
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
from setuptools import setup

import sys

import twine


install_requires = [
    "requests",
    "pkginfo",
]

if sys.version_info[:2] < (2, 7):
    install_requires += [
        "argparse",
    ]


setup(
    name=twine.__title__,
    version=twine.__version__,

    description=twine.__summary__,
    long_description=open("README.rst").read(),
    license=twine.__license__,
    url=twine.__uri__,

    author=twine.__author__,
    author_email=twine.__email__,

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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],

    packages=["twine", "twine.commands"],

    entry_points={
        "console_scripts": [
            "twine = twine.__main__:main",
            "twine-upload = twine.commands.upload:main",
        ],
    },

    install_requires=install_requires,
)
