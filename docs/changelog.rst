=========
Changelog
=========

This project follows the `semantic versioning <https://packaging.python.org/guides/distributing-packages-using-setuptools/#semantic-versioning-preferred>`_
and `pre-release versioning <https://packaging.python.org/guides/distributing-packages-using-setuptools/#pre-release-versioning>`_
schemes recommended by the Python Packaging Authority.

.. Do *NOT* add changelog entries here!
   This changelog is managed by towncrier and is built at release time.
   See https://twine.readthedocs.io/en/latest/contributing.html#changelog-entries for details.

.. towncrier release notes start

3.4.0 (2021-03-13)
------------------

Features
^^^^^^^^

- Prefer importlib.metadata for entry point handling. (`#728 <https://github.com/pypa/twine/issues/728>`_)
- Rely on importlib_metadata 3.6 for nicer entry point processing. (`#732 <https://github.com/pypa/twine/issues/732>`_)
- Eliminated dependency on Setuptools/pkg_resources and replaced with packaging and importlib_metadata. (`#736 <https://github.com/pypa/twine/issues/736>`_)


3.3.0 (2020-12-23)
------------------

Features
^^^^^^^^

- Print files to be uploaded using ``upload --verbose`` (`#670 <https://github.com/pypa/twine/issues/670>`_)
- Print configuration file location when using ``upload --verbose`` (`#675 <https://github.com/pypa/twine/issues/675>`_)
- Print source and values of credentials when using ``upload --verbose`` (`#685 <https://github.com/pypa/twine/issues/685>`_)
- Add support for Python 3.9 (`#708 <https://github.com/pypa/twine/issues/708>`_)
- Turn warnings into errors when using ``check --strict`` (`#715 <https://github.com/pypa/twine/issues/715>`_)


Bugfixes
^^^^^^^^

- Make password optional when using ``upload --client-cert`` (`#678 <https://github.com/pypa/twine/issues/678>`_)
- Support more Nexus versions with ``upload --skip-existing`` (`#693 <https://github.com/pypa/twine/issues/693>`_)
- Support Gitlab Enterprise with ``upload --skip-existing`` (`#698 <https://github.com/pypa/twine/issues/698>`_)
- Show a better error message for malformed files (`#714 <https://github.com/pypa/twine/issues/714>`_)


Improved Documentation
^^^^^^^^^^^^^^^^^^^^^^

- Adopt PSF code of conduct (`#680 <https://github.com/pypa/twine/issues/680>`_)
- Adopt towncrier for the changleog (`#718 <https://github.com/pypa/twine/issues/718>`_)


3.2.0 (2020-06-24)
------------------

Features
^^^^^^^^

- Improve display of HTTP errors during upload (`#666 <https://github.com/pypa/twine/issues/666>`_)
- Print packages and signatures to be uploaded when using ``--verbose`` option (`#652 <https://github.com/pypa/twine/issues/652>`_)
- Use red text when printing errors on the command line (`#649 <https://github.com/pypa/twine/issues/649>`_)
- Require repository URL scheme to be ``http`` or ``https`` (`#602 <https://github.com/pypa/twine/issues/602>`_)
- Add type annotations, checked with mypy, with :pep:`561` support for users of Twine's API (`#231 <https://github.com/pypa/twine/issues/231>`_)

Bugfixes
^^^^^^^^

- Update URL to ``.pypirc`` specification (`#655 <https://github.com/pypa/twine/issues/655>`_)
- Don't raise an exception when Python version can't be parsed from filename (`#612 <https://github.com/pypa/twine/issues/612>`_)
- Fix inaccurate retry message during ``upload`` (`#611 <https://github.com/pypa/twine/issues/611>`_)
- Clarify error messages for archive format (`#601 <https://github.com/pypa/twine/issues/601>`_)

3.1.1 (2019-11-27)
------------------

Bugfixes
^^^^^^^^

- Restore ``--non-interactive`` as a flag not expecting an argument. (`#548 <https://github.com/pypa/twine/issues/548>`_)

3.1.0 (2019-11-23)
------------------

Features
^^^^^^^^

- Add support for specifying ``--non-interactive`` as an environment variable. (`#547 <https://github.com/pypa/twine/issues/547>`_)

3.0.0 (2019-11-18)
------------------

Features
^^^^^^^^

- When a client certificate is indicated, all password processing is disabled. (`#336 <https://github.com/pypa/twine/issues/336>`_)
- Add ``--non-interactive`` flag to abort upload rather than interactively prompt if credentials are missing. (`#489 <https://github.com/pypa/twine/issues/489>`_)
- Twine now unconditionally requires the keyring library and no longer supports uninstalling ``keyring`` as a means to disable that functionality. Instead, use ``keyring --disable`` keyring functionality if necessary. (`#524 <https://github.com/pypa/twine/issues/524>`_)
- Add Python 3.8 to classifiers. (`#518 <https://github.com/pypa/twine/issues/518>`_)

Bugfixes
^^^^^^^^

- More robust handling of server response in ``--skip-existing`` (`#332 <https://github.com/pypa/twine/issues/332>`_)

2.0.0 (2019-09-24)
------------------

Features
^^^^^^^^

- Twine now requires Python 3.6 or later. Use pip 9 or pin to "twine<2" to install twine on older Python versions. (`#437 <https://github.com/pypa/twine/issues/437>`_)

Bugfixes
^^^^^^^^

- Require requests 2.20 or later to avoid reported security vulnerabilities in earlier releases. (`#491 <https://github.com/pypa/twine/issues/491>`_)

1.15.0 (2019-09-17)
-------------------

Features
^^^^^^^^

- Improved output on ``check`` command: Prints a message when there are no distributions given to check. Improved handling of errors in a distribution's markup, avoiding messages flowing through to the next distribution's errors. (`#488 <https://github.com/pypa/twine/issues/488>`_)

1.14.0 (2019-09-06)
-------------------

Features
^^^^^^^^

- Show Warehouse URL after uploading a package (`#459 <https://github.com/pypa/twine/issues/459>`_)
- Better error handling and gpg2 fallback if gpg not available. (`#456 <https://github.com/pypa/twine/issues/456>`_)
- Now provide a more meaningful error on redirect during upload. (`#310 <https://github.com/pypa/twine/issues/310>`_)

Bugfixes
^^^^^^^^

- Fail more gracefully when encountering bad metadata (`#341 <https://github.com/pypa/twine/issues/341>`_)

1.13.0 (2019-02-13)
-------------------

Features
^^^^^^^^

- Add disable_progress_bar option to disable tqdm. (`#427 <https://github.com/pypa/twine/issues/427>`_)
- Allow defining an empty username and password in .pypirc. (`#426 <https://github.com/pypa/twine/issues/426>`_)
- Support keyring.get_credential. (`#419 <https://github.com/pypa/twine/issues/419>`_)
- Support keyring.get_username_and_password. (`#418 <https://github.com/pypa/twine/issues/418>`_)
- Add Python 3.7 to classifiers. (`#416 <https://github.com/pypa/twine/issues/416>`_)

Bugfixes
^^^^^^^^

- Restore prompts while retaining support for suppressing prompts. (`#452 <https://github.com/pypa/twine/issues/452>`_)
- Avoid requests-toolbelt to 0.9.0 to prevent attempting to use openssl when it isn't available. (`#447 <https://github.com/pypa/twine/issues/447>`_)
- Use io.StringIO instead of StringIO. (`#444 <https://github.com/pypa/twine/issues/444>`_)
- Only install pyblake2 if needed. (`#441 <https://github.com/pypa/twine/issues/441>`_)
- Use modern Python language features. (`#436 <https://github.com/pypa/twine/issues/436>`_)
- Specify python_requires in setup.py (`#435 <https://github.com/pypa/twine/issues/435>`_)
- Use https URLs everywhere. (`#432 <https://github.com/pypa/twine/issues/432>`_)
- Fix --skip-existing for Nexus Repos. (`#428 <https://github.com/pypa/twine/issues/428>`_)
- Remove unnecessary usage of readme_render.markdown. (`#421 <https://github.com/pypa/twine/issues/421>`_)
- Don't crash if there's no package description. (`#412 <https://github.com/pypa/twine/issues/412>`_)
- Fix keyring support. (`#408 <https://github.com/pypa/twine/issues/408>`_)

Misc
^^^^

- Refactor tox env and travis config. (`#439 <https://github.com/pypa/twine/issues/439>`_)

1.12.1 (2018-09-24)
-------------------

Bugfixes
^^^^^^^^

- Fix regression with upload exit code (`#404 <https://github.com/pypa/twine/issues/404>`_)

1.12.0 (2018-09-24)
-------------------

Features
^^^^^^^^

- Add ``twine check`` command to check long description (`#395 <https://github.com/pypa/twine/issues/395>`_)
- Drop support for Python 3.3 (`#392 <https://github.com/pypa/twine/issues/392>`_)
- Empower ``--skip-existing`` for Artifactory repositories (`#363 <https://github.com/pypa/twine/issues/363>`_)

Bugfixes
^^^^^^^^

- Avoid MD5 when Python is compiled in FIPS mode (`#367 <https://github.com/pypa/twine/issues/367>`_)

1.11.0 (2018-03-19)
-------------------

Features
^^^^^^^^

- Remove PyPI as default ``register`` package index. (`#320 <https://github.com/pypa/twine/issues/320>`_)
- Support Metadata 2.1 (:pep:`566`), including Markdown for ``description`` fields. (`#319 <https://github.com/pypa/twine/issues/319>`_)

Bugfixes
^^^^^^^^

- Raise exception if attempting upload to deprecated legacy PyPI URLs. (`#322 <https://github.com/pypa/twine/issues/322>`_)
- Avoid uploading to PyPI when given alternate repository URL, and require ``http://`` or ``https://`` in ``repository_url``. (`#269 <https://github.com/pypa/twine/issues/269>`_)

Misc
^^^^

- `Update PyPI URLs <https://packaging.python.org/guides/migrating-to-pypi-org/>`_. (`#318 <https://github.com/pypa/twine/issues/318>`_)
- Add new maintainer, release checklists. (`#314 <https://github.com/pypa/twine/issues/314>`_)
- Add instructions on how to use keyring. (`#277 <https://github.com/pypa/twine/issues/277>`_)

1.10.0 (2018-03-07)
-------------------

Features
^^^^^^^^

- Link to changelog from ``README`` (`#46 <https://github.com/pypa/twine/issues/46>`_)
- Reorganize & improve user & developer documentation. (`#304 <https://github.com/pypa/twine/issues/304>`_)
- Revise docs predicting future of ``twine`` (`#303 <https://github.com/pypa/twine/issues/303>`_)
- Add architecture overview to docs (`#296 <https://github.com/pypa/twine/issues/296>`_)
- Add doc building instructions (`#295 <https://github.com/pypa/twine/issues/295>`_)
- Declare support for Python 3.6 (`#257 <https://github.com/pypa/twine/issues/257>`_)
- Improve progressbar (`#256 <https://github.com/pypa/twine/issues/256>`_)

Bugfixes
^^^^^^^^

- Degrade gracefully when keyring is unavailable (`#315 <https://github.com/pypa/twine/issues/315>`_)
- Fix changelog formatting (`#299 <https://github.com/pypa/twine/issues/299>`_)
- Fix syntax highlighting in ``README`` (`#298 <https://github.com/pypa/twine/issues/298>`_)
- Fix Read the Docs, tox, Travis configuration (`#297 <https://github.com/pypa/twine/issues/297>`_)
- Fix Travis CI and test configuration (`#286 <https://github.com/pypa/twine/issues/286>`_)
- Print progress to ``stdout``, not ``stderr`` (`#268 <https://github.com/pypa/twine/issues/268>`_)
- Fix ``--repository[-url]`` help text (`#265 <https://github.com/pypa/twine/issues/265>`_)
- Remove obsolete registration guidance (`#200 <https://github.com/pypa/twine/issues/200>`_)

1.9.1 (2017-05-27)
------------------

Bugfixes
^^^^^^^^

- Blacklist known bad versions of Requests. (`#253 <https://github.com/pypa/twine/issues/253>`_)

1.9.0 (2017-05-22)
------------------

Bugfixes
^^^^^^^^

- Twine sends less information about the user's system in the User-Agent string. (`#229 <https://github.com/pypa/twine/issues/229>`_)
- Fix ``--skip-existing`` when used to upload a package for the first time. (`#220 <https://github.com/pypa/twine/issues/220>`_)
- Fix precedence of ``--repository-url`` over ``--repository``. (`#206 <https://github.com/pypa/twine/issues/206>`_)

Misc
^^^^

- Twine will now resolve passwords using the `keyring <https://pypi.org/project/keyring/>`_ if available. Module can be required with the ``keyring`` extra.
- Twine will use ``hashlib.blake2b`` on Python 3.6+ instead of pyblake2

1.8.1 (2016-08-09)
------------------

Misc
^^^^

- Check if a package exists if the URL is one of:

    * ``https://pypi.python.org/pypi/``
    * ``https://upload.pypi.org/``
    * ``https://upload.pypi.io/``

    This helps people with ``https://upload.pypi.io`` still in their
    :file:`.pypirc` file.


1.8.0 (2016-08-08)
------------------

Features
^^^^^^^^

- Switch from upload.pypi.io to upload.pypi.org. (`#201 <https://github.com/pypa/twine/issues/201>`_)
- Retrieve configuration from the environment as a default. (`#144 <https://github.com/pypa/twine/issues/144>`_)

    * Repository URL will default to ``TWINE_REPOSITORY``
    * Username will default to ``TWINE_USERNAME``
    * Password will default to ``TWINE_PASSWORD``

- Allow the Repository URL to be provided on the command-line (``--repository-url``) or via an environment variable (``TWINE_REPOSITORY_URL``). (`#166 <https://github.com/pypa/twine/issues/166>`_)
- Generate Blake2b 256 digests for packages *if* ``pyblake2`` is installed. Users can use ``python -m pip install twine[with-blake2]`` to have ``pyblake2`` installed with Twine. (`#171 <https://github.com/pypa/twine/issues/171>`_)

Misc
^^^^

- Generate SHA256 digest for all packages by default.
- Stop testing on Python 2.6.
- Warn users if they receive a 500 error when uploading to ``*pypi.python.org`` (`#199 <https://github.com/pypa/twine/issues/199>`_)

1.7.4 (2016-07-09)
------------------

Bugfixes
^^^^^^^^

- Correct a packaging error.

1.7.3 (2016-07-08)
------------------

Bugfixes
^^^^^^^^

- Fix uploads to instances of pypiserver using ``--skip-existing``. We were not properly checking the return status code on the response after attempting an upload. (`#195 <https://github.com/pypa/twine/issues/195>`_)

Misc
^^^^

- Avoid attempts to upload a package if we can find it on Legacy PyPI.

1.7.2 (2016-07-05)
------------------

Bugfixes
^^^^^^^^

- Fix issue where we were checking the existence of packages even if the user didn't specify ``--skip-existing``. (`#189 <https://github.com/pypa/twine/issues/189>`_) (`#191 <https://github.com/pypa/twine/issues/191>`_)

1.7.1 (2016-07-05)
------------------

Bugfixes
^^^^^^^^

- Clint was not specified in the wheel metadata as a dependency. (`#187 <https://github.com/pypa/twine/issues/187>`_)

1.7.0 (2016-07-04)
------------------

Features
^^^^^^^^

- Support ``--cert`` and ``--client-cert`` command-line flags and config file options for feature parity with pip. This allows users to verify connections to servers other than PyPI (e.g., local package repositories) with different certificates. (`#142 <https://github.com/pypa/twine/issues/142>`_)
- Add progress bar to uploads. (`#152 <https://github.com/pypa/twine/issues/152>`_)
- Allow ``--skip-existing`` to work for 409 status codes. (`#162 <https://github.com/pypa/twine/issues/162>`_)
- Implement retries when the CDN in front of PyPI gives us a 5xx error. (`#167 <https://github.com/pypa/twine/issues/167>`_)
- Switch Twine to upload to pypi.io instead of pypi.python.org. (`#177 <https://github.com/pypa/twine/issues/177>`_)

Bugfixes
^^^^^^^^

- Allow passwords to have ``%``\ s in them. (`#186 <https://github.com/pypa/twine/issues/186>`_)

1.6.5 (2015-12-16)
------------------

Bugfixes
^^^^^^^^

- Bump requests-toolbelt version to ensure we avoid ConnectionErrors (`#155 <https://github.com/pypa/twine/issues/155>`_)

1.6.4 (2015-10-27)
------------------

Bugfixes
^^^^^^^^

- Paths with hyphens in them break the Wheel regular expression. (`#145 <https://github.com/pypa/twine/issues/145>`_)
- Exception while accessing the ``repository`` key (sic) when raising a redirect exception. (`#146 <https://github.com/pypa/twine/issues/146>`_)

1.6.3 (2015-10-05)
------------------

Bugfixes
^^^^^^^^

- Fix uploading signatures causing a 500 error after large file support was added. (`#137 <https://github.com/pypa/twine/issues/137>`_, `#140 <https://github.com/pypa/twine/issues/140>`_)

1.6.2 (2015-09-28)
------------------

Bugfixes
^^^^^^^^

- Upload signatures with packages appropriately (`#132 <https://github.com/pypa/twine/issues/132>`_)

    As part of the refactor for the 1.6.0 release, we were using the wrong
    name to find the signature file.

    This also uncovered a bug where if you're using twine in a situation where
    ``*`` is not expanded by your shell, we might also miss uploading
    signatures to PyPI. Both were fixed as part of this.


1.6.1 (2015-09-18)
------------------

Bugfixes
^^^^^^^^

- Fix signing support for uploads (`#130 <https://github.com/pypa/twine/issues/130>`_)

1.6.0 (2015-09-14)
------------------

Features
^^^^^^^^

- Allow the user to specify the location of their :file:`.pypirc` (`#97 <https://github.com/pypa/twine/issues/97>`_)
- Support registering new packages with ``twine register`` (`#8 <https://github.com/pypa/twine/issues/8>`_)
- Add the ``--skip-existing`` flag to ``twine upload`` to allow users to skip releases that already exist on PyPI. (`#115 <https://github.com/pypa/twine/issues/115>`_)
- Upload wheels first to PyPI (`#106 <https://github.com/pypa/twine/issues/106>`_)
- Large file support via the ``requests-toolbelt`` (`#104 <https://github.com/pypa/twine/issues/104>`_)

Bugfixes
^^^^^^^^

- Raise an exception on redirects (`#92 <https://github.com/pypa/twine/issues/92>`_)
- Work around problems with Windows when using ``getpass.getpass`` (`#116 <https://github.com/pypa/twine/issues/116>`_)
- Warnings triggered by pkginfo searching for ``PKG-INFO`` files should no longer be user visible. (`#114 <https://github.com/pypa/twine/issues/114>`_)
- Provide more helpful messages if :file:`.pypirc` is out of date. (`#111 <https://github.com/pypa/twine/issues/111>`_)

1.5.0 (2015-03-10)
------------------

Features
^^^^^^^^

- Support commands not named "gpg" for signing (`#29 <https://github.com/pypa/twine/issues/29>`_)

Bugfixes
^^^^^^^^

- Display information about the version of setuptools installed (`#85 <https://github.com/pypa/twine/issues/85>`_)
- Support deprecated pypirc file format (`#61 <https://github.com/pypa/twine/issues/61>`_)

Misc
^^^^

- Add lower-limit to requests dependency

1.4.0 (2014-12-12)
------------------

Features
^^^^^^^^

- Switch to a git style dispatching for the commands to enable simpler commands and programmatic invocation. (`#6 <https://github.com/pypa/twine/issues/6>`_)
- Parse :file:`~/.pypirc` ourselves and use ``subprocess`` instead of the ``distutils.spawn`` module. (`#13 <https://github.com/pypa/twine/issues/13>`_)

Bugfixes
^^^^^^^^

- Expand globs and check for existence of dists to upload (`#65 <https://github.com/pypa/twine/issues/65>`_)
- Fix issue uploading packages with ``_``\ s in the name (`#47 <https://github.com/pypa/twine/issues/47>`_)
- List registered commands in help text (`#34 <https://github.com/pypa/twine/issues/34>`_)
- Use ``pkg_resources`` to load registered commands (`#32 <https://github.com/pypa/twine/issues/32>`_)
- Prevent ResourceWarning from being shown (`#28 <https://github.com/pypa/twine/issues/28>`_)
- Add support for uploading Windows installers (`#26 <https://github.com/pypa/twine/issues/26>`_)

1.3.0 (2014-03-31)
------------------

Features
^^^^^^^^

- Additional functionality.

1.2.2 (2013-10-03)
------------------

Features
^^^^^^^^

- Basic functionality.
