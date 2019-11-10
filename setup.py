from setuptools import setup

import twine


setup(
    name=twine.__title__,
    version=twine.__version__,

    description=twine.__summary__,
    long_description=open("README.rst").read(),
    license=twine.__license__,
    url=twine.__uri__,
    project_urls={
        'Packaging tutorial': 'https://packaging.python.org/tutorials/distributing-packages/',
        'Travis CI': 'https://travis-ci.org/pypa/twine',
        'Twine documentation': 'https://twine.readthedocs.io/en/latest/',
        'Twine source': 'https://github.com/pypa/twine/',
    },

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
    ],
    extras_require={
        'keyring': [
            'keyring',
        ],
    },
)
