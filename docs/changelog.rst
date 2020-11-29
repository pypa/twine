=========
Changelog
=========

3.2.0 (2020-06-24)
------------------

- *Feature* Improve display of HTTP errors during upload (`#666 <https://github.com/pypa/twine/issues/666>`_)
- *Feature* Print packages and signatures to be uploaded when using ``--verbose`` option (`#652 <https://github.com/pypa/twine/issues/652>`_)
- *Feature* Use red text when printing errors on the command line (`#649 <https://github.com/pypa/twine/issues/649>`_)
- *Feature* Require repository URL scheme to be ``http`` or ``https`` (`#602 <https://github.com/pypa/twine/issues/602>`_)
- *Feature* Add type annotations, checked with mypy, with :pep:`561` support for users of Twine's API (`#231 <https://github.com/pypa/twine/issues/231>`_)
- *Bugfix* Update URL to ``.pypirc`` specification (`#655 <https://github.com/pypa/twine/issues/655>`_)
- *Bugfix* Don't raise an exception when Python version can't be parsed from filename (`#612 <https://github.com/pypa/twine/issues/612>`_)
- *Bugfix* Fix inaccurate retry message during ``upload`` (`#611 <https://github.com/pypa/twine/issues/611>`_)
- *Bugfix* Clarify error messages for archive format (`#601 <https://github.com/pypa/twine/issues/601>`_)

3.1.1 (2019-11-27)
------------------

- *Bugfix* Restore ``--non-interactive`` as a flag not expecting an argument. (`#548 <https://github.com/pypa/twine/issues/548>`_)

3.1.0 (2019-11-23)
------------------

- *Feature* Add support for specifying ``--non-interactive`` as an environment variable. (`#547 <https://github.com/pypa/twine/issues/547>`_)

3.0.0 (2019-11-18)
------------------

- *Feature* When a client certificate is indicated, all password processing is disabled. (`#336 <https://github.com/pypa/twine/issues/336>`_)
- *Feature* Add ``--non-interactive`` flag to abort upload rather than interactively prompt if credentials are missing. (`#489 <https://github.com/pypa/twine/issues/489>`_)
- *Feature* Twine now unconditionally requires the keyring library and no longer supports uninstalling ``keyring`` as a means to disable that functionality. Instead, use ``keyring --disable`` keyring functionality if necessary. (`#524 <https://github.com/pypa/twine/issues/524>`_)
- *Feature* Add Python 3.8 to classifiers. (`#518 <https://github.com/pypa/twine/issues/518>`_)
- *Bugfix* More robust handling of server response in ``--skip-existing`` (`#332 <https://github.com/pypa/twine/issues/332>`_)

2.0.0 (2019-09-24)
------------------

- *Feature* Twine now requires Python 3.6 or later. Use pip 9 or pin to "twine<2" to install twine on older Python versions. (`#437 <https://github.com/pypa/twine/issues/437>`_)
- *Bugfix* Require requests 2.20 or later to avoid reported security vulnerabilities in earlier releases. (`#491 <https://github.com/pypa/twine/issues/491>`_)

1.15.0 (2019-09-17)
-------------------

- *Feature* Improved output on ``check`` command: Prints a message when there are no distributions given to check. Improved handling of errors in a distribution's markup, avoiding messages flowing through to the next distribution's errors. (`#488 <https://github.com/pypa/twine/issues/488>`_)

1.14.0 (2019-09-06)
-------------------

- *Feature* Show Warehouse URL after uploading a package (`#459 <https://github.com/pypa/twine/issues/459>`_)
- *Feature* Better error handling and gpg2 fallback if gpg not available. (`#456 <https://github.com/pypa/twine/issues/456>`_)
- *Feature* Now provide a more meaningful error on redirect during upload. (`#310 <https://github.com/pypa/twine/issues/310>`_)
- *Bugfix* Fail more gracefully when encountering bad metadata (`#341 <https://github.com/pypa/twine/issues/341>`_)

1.13.0 (2019-02-13)
-------------------

- *Feature* Add disable_progress_bar option to disable tqdm. (`#427 <https://github.com/pypa/twine/issues/427>`_)
- *Feature* Allow defining an empty username and password in .pypirc. (`#426 <https://github.com/pypa/twine/issues/426>`_)
- *Feature* Support keyring.get_credential. (`#419 <https://github.com/pypa/twine/issues/419>`_)
- *Feature* Support keyring.get_username_and_password. (`#418 <https://github.com/pypa/twine/issues/418>`_)
- *Feature* Add Python 3.7 to classifiers. (`#416 <https://github.com/pypa/twine/issues/416>`_)
- *Bugfix* Restore prompts while retaining support for suppressing prompts. (`#452 <https://github.com/pypa/twine/issues/452>`_)
- *Bugfix* Avoid requests-toolbelt to 0.9.0 to prevent attempting to use openssl when it isn't available. (`#447 <https://github.com/pypa/twine/issues/447>`_)
- *Bugfix* Use io.StringIO instead of StringIO. (`#444 <https://github.com/pypa/twine/issues/444>`_)
- *Bugfix* Only install pyblake2 if needed. (`#441 <https://github.com/pypa/twine/issues/441>`_)
- *Bugfix* Use modern Python language features. (`#436 <https://github.com/pypa/twine/issues/436>`_)
- *Bugfix* Specify python_requires in setup.py (`#435 <https://github.com/pypa/twine/issues/435>`_)
- *Bugfix* Use https URLs everywhere. (`#432 <https://github.com/pypa/twine/issues/432>`_)
- *Bugfix* Fix --skip-existing for Nexus Repos. (`#428 <https://github.com/pypa/twine/issues/428>`_)
- *Bugfix* Remove unnecessary usage of readme_render.markdown. (`#421 <https://github.com/pypa/twine/issues/421>`_)
- *Bugfix* Don't crash if there's no package description. (`#412 <https://github.com/pypa/twine/issues/412>`_)
- *Bugfix* Fix keyring support. (`#408 <https://github.com/pypa/twine/issues/408>`_)
- *Misc* Refactor tox env and travis config. (`#439 <https://github.com/pypa/twine/issues/439>`_)

1.12.1 (2018-09-24)
-------------------

- *Bugfix* Fix regression with upload exit code (`#404 <https://github.com/pypa/twine/issues/404>`_)

1.12.0 (2018-09-24)
-------------------

- *Feature* Add ``twine check`` command to check long description (`#395 <https://github.com/pypa/twine/issues/395>`_)
- *Feature* Drop support for Python 3.3 (`#392 <https://github.com/pypa/twine/issues/392>`_)
- *Feature* Empower ``--skip-existing`` for Artifactory repositories (`#363 <https://github.com/pypa/twine/issues/363>`_)
- *Bugfix* Avoid MD5 when Python is compiled in FIPS mode (`#367 <https://github.com/pypa/twine/issues/367>`_)

1.11.0 (2018-03-19)
-------------------

- *Feature* Remove PyPI as default ``register`` package index. (`#320 <https://github.com/pypa/twine/issues/320>`_)
- *Feature* Support Metadata 2.1 (:pep:`566`), including Markdown for ``description`` fields. (`#319 <https://github.com/pypa/twine/issues/319>`_)
- *Bugfix* Raise exception if attempting upload to deprecated legacy PyPI URLs. (`#322 <https://github.com/pypa/twine/issues/322>`_)
- *Bugfix* Avoid uploading to PyPI when given alternate repository URL, and require ``http://`` or ``https://`` in ``repository_url``. (`#269 <https://github.com/pypa/twine/issues/269>`_)
- *Misc* `Update PyPI URLs <https://packaging.python.org/guides/migrating-to-pypi-org/>`_. (`#318 <https://github.com/pypa/twine/issues/318>`_)
- *Misc* Add new maintainer, release checklists. (`#314 <https://github.com/pypa/twine/issues/314>`_)
- *Misc* Add instructions on how to use keyring. (`#277 <https://github.com/pypa/twine/issues/277>`_)

1.10.0 (2018-03-07)
-------------------

- *Feature* Link to changelog from ``README`` (`#46 <https://github.com/pypa/twine/issues/46>`_)
- *Feature* Reorganize & improve user & developer documentation. (`#304 <https://github.com/pypa/twine/issues/304>`_)
- *Feature* Revise docs predicting future of ``twine`` (`#303 <https://github.com/pypa/twine/issues/303>`_)
- *Feature* Add architecture overview to docs (`#296 <https://github.com/pypa/twine/issues/296>`_)
- *Feature* Add doc building instructions (`#295 <https://github.com/pypa/twine/issues/295>`_)
- *Feature* Declare support for Python 3.6 (`#257 <https://github.com/pypa/twine/issues/257>`_)
- *Feature* Improve progressbar (`#256 <https://github.com/pypa/twine/issues/256>`_)
- *Bugfix* Degrade gracefully when keyring is unavailable (`#315 <https://github.com/pypa/twine/issues/315>`_)
- *Bugfix* Fix changelog formatting (`#299 <https://github.com/pypa/twine/issues/299>`_)
- *Bugfix* Fix syntax highlighting in ``README`` (`#298 <https://github.com/pypa/twine/issues/298>`_)
- *Bugfix* Fix Read the Docs, tox, Travis configuration (`#297 <https://github.com/pypa/twine/issues/297>`_)
- *Bugfix* Fix Travis CI and test configuration (`#286 <https://github.com/pypa/twine/issues/286>`_)
- *Bugfix* Print progress to ``stdout``, not ``stderr`` (`#268 <https://github.com/pypa/twine/issues/268>`_)
- *Bugfix* Fix ``--repository[-url]`` help text (`#265 <https://github.com/pypa/twine/issues/265>`_)
- *Bugfix* Remove obsolete registration guidance (`#200 <https://github.com/pypa/twine/issues/200>`_)

1.9.1 (2017-05-27)
------------------

- *Bugfix* Blacklist known bad versions of Requests. (`#253 <https://github.com/pypa/twine/issues/253>`_)

1.9.0 (2017-05-22)
------------------

- *Bugfix* Twine sends less information about the user's system in the User-Agent string. (`#229 <https://github.com/pypa/twine/issues/229>`_)
- *Bugfix* Fix ``--skip-existing`` when used to upload a package for the first time. (`#220 <https://github.com/pypa/twine/issues/220>`_)
- *Bugfix* Fix precedence of ``--repository-url`` over ``--repository``. (`#206 <https://github.com/pypa/twine/issues/206>`_)
- *Misc* Twine will now resolve passwords using the `keyring <https://pypi.org/project/keyring/>`_ if available. Module can be required with the ``keyring`` extra.
- *Misc* Twine will use ``hashlib.blake2b`` on Python 3.6+ instead of using pyblake2 for Blake2 hashes 256 bit hashes.

1.8.1 (2016-08-09)
------------------

- *Misc* Check if a package exists if the URL is one of:

    * ``https://pypi.python.org/pypi/``
    * ``https://upload.pypi.org/``
    * ``https://upload.pypi.io/``

    This helps people with ``https://upload.pypi.io`` still in their
    :file:`.pypirc` file.


1.8.0 (2016-08-08)
------------------

- *Feature* Switch from upload.pypi.io to upload.pypi.org. (`#201 <https://github.com/pypa/twine/issues/201>`_)
- *Feature* Retrieve configuration from the environment as a default. (`#144 <https://github.com/pypa/twine/issues/144>`_)

    * Repository URL will default to ``TWINE_REPOSITORY``
    * Username will default to ``TWINE_USERNAME``
    * Password will default to ``TWINE_PASSWORD``

- *Feature* Allow the Repository URL to be provided on the command-line (``--repository-url``) or via an environment variable (``TWINE_REPOSITORY_URL``). (`#166 <https://github.com/pypa/twine/issues/166>`_)
- *Feature* Generate Blake2b 256 digests for packages *if* ``pyblake2`` is installed. Users can use ``python -m pip install twine[with-blake2]`` to have ``pyblake2`` installed with Twine. (`#171 <https://github.com/pypa/twine/issues/171>`_)
- *Misc* Generate SHA256 digest for all packages by default.
- *Misc* Stop testing on Python 2.6. 2.6 support will be "best effort" until 2.0.0
- *Misc* Warn users if they receive a 500 error when uploading to ``*pypi.python.org``

1.7.4 (2016-07-09)
------------------

- *Bugfix* Correct a packaging error.

1.7.3 (2016-07-08)
------------------

- *Bugfix* Fix uploads to instances of pypiserver using ``--skip-existing``. We were not properly checking the return status code on the response after attempting an upload. (`#195 <https://github.com/pypa/twine/issues/195>`_)
- *Misc* Do not generate traffic to Legacy PyPI unless we're uploading to it or uploading to Warehouse (e.g., pypi.io). This avoids the attempt to upload a package to the index if we can find it on Legacy PyPI already.

1.7.2 (2016-07-05)
------------------

- *Bugfix* Fix issue where we were checking the existence of packages even if the user didn't specify ``--skip-existing``. (`#189 <https://github.com/pypa/twine/issues/189>`_) (`#191 <https://github.com/pypa/twine/issues/191>`_)

1.7.1 (2016-07-05)
------------------

- *Bugfix* Clint was not specified in the wheel metadata as a dependency. (`#187 <https://github.com/pypa/twine/issues/187>`_)

1.7.0 (2016-07-04)
------------------

- *Feature* Support ``--cert`` and ``--client-cert`` command-line flags and config file options for feature parity with pip. This allows users to verify connections to servers other than PyPI (e.g., local package repositories) with different certificates. (`#142 <https://github.com/pypa/twine/issues/142>`_)
- *Feature* Add progress bar to uploads. (`#152 <https://github.com/pypa/twine/issues/152>`_)
- *Feature* Allow ``--skip-existing`` to work for 409 status codes. (`#162 <https://github.com/pypa/twine/issues/162>`_)
- *Feature* Implement retries when the CDN in front of PyPI gives us a 5xx error. (`#167 <https://github.com/pypa/twine/issues/167>`_)
- *Feature* Switch Twine to upload to pypi.io instead of pypi.python.org. (`#177 <https://github.com/pypa/twine/issues/177>`_)
- *Bugfix* Allow passwords to have ``%``\ s in them. (`#186 <https://github.com/pypa/twine/issues/186>`_)

1.6.5 (2015-12-16)
------------------

- *Bugfix* Bump requests-toolbelt version to ensure we avoid ConnectionErrors (`#155 <https://github.com/pypa/twine/issues/155>`_)

1.6.4 (2015-10-27)
------------------

- *Bugfix* Paths with hyphens in them break the Wheel regular expression. (`#145 <https://github.com/pypa/twine/issues/145>`_)
- *Bugfix* Exception while accessing the ``repository`` key (sic) when raising a redirect exception. (`#146 <https://github.com/pypa/twine/issues/146>`_)

1.6.3 (2015-10-05)
------------------

- *Bugfix* Uploading signatures was broken due to the pull request that added large file support via ``requests-toolbelt``. This caused a 500 error on PyPI and prevented package and signature upload in twine 1.6.0 (`137`, `140`)

1.6.2 (2015-09-28)
------------------

- *Bugfix* Upload signatures with packages appropriately (`#132 <https://github.com/pypa/twine/issues/132>`_)

    As part of the refactor for the 1.6.0 release, we were using the wrong
    name to find the signature file.

    This also uncovered a bug where if you're using twine in a situation where
    ``*`` is not expanded by your shell, we might also miss uploading
    signatures to PyPI. Both were fixed as part of this.


1.6.1 (2015-09-18)
------------------

- *Bugfix* Fix signing support for uploads (`#130 <https://github.com/pypa/twine/issues/130>`_)

1.6.0 (2015-09-14)
------------------

- *Feature* Allow the user to specify the location of their :file:`.pypirc` (`#97 <https://github.com/pypa/twine/issues/97>`_)
- *Feature* Support registering new packages with ``twine register`` (`#8 <https://github.com/pypa/twine/issues/8>`_)
- *Feature* Add the ``--skip-existing`` flag to ``twine upload`` to allow users to skip releases that already exist on PyPI. (`#115 <https://github.com/pypa/twine/issues/115>`_)
- *Feature* Upload wheels first to PyPI (`#106 <https://github.com/pypa/twine/issues/106>`_)
- *Feature* Large file support via the ``requests-toolbelt`` (`#104 <https://github.com/pypa/twine/issues/104>`_)
- *Bugfix* Raise an exception on redirects (`#92 <https://github.com/pypa/twine/issues/92>`_)
- *Bugfix* Work around problems with Windows when using ``getpass.getpass`` (`#116 <https://github.com/pypa/twine/issues/116>`_)
- *Bugfix* Warnings triggered by pkginfo searching for ``PKG-INFO`` files should no longer be user visible. (`#114 <https://github.com/pypa/twine/issues/114>`_)
- *Bugfix* Provide more helpful messages if :file:`.pypirc` is out of date. (`#111 <https://github.com/pypa/twine/issues/111>`_)

1.5.0 (2015-03-10)
------------------

- *Feature* Support commands not named "gpg" for signing (`#29 <https://github.com/pypa/twine/issues/29>`_)
- *Bugfix* Display information about the version of setuptools installed (`#85 <https://github.com/pypa/twine/issues/85>`_)
- *Bugfix* Support deprecated pypirc file format (`#61 <https://github.com/pypa/twine/issues/61>`_)
- *Misc* Add lower-limit to requests dependency

1.4.0 (2014-12-12)
------------------

- *Feature* Switch to a git style dispatching for the commands to enable simpler commands and programmatic invocation. (`#6 <https://github.com/pypa/twine/issues/6>`_)
- *Feature* Parse :file:`~/.pypirc` ourselves and use ``subprocess`` instead of the ``distutils.spawn`` module. (`#13 <https://github.com/pypa/twine/issues/13>`_)
- *Bugfix* Expand globs and check for existence of dists to upload (`#65 <https://github.com/pypa/twine/issues/65>`_)
- *Bugfix* Fix issue uploading packages with ``_``\ s in the name (`#47 <https://github.com/pypa/twine/issues/47>`_)
- *Bugfix* List registered commands in help text (`#34 <https://github.com/pypa/twine/issues/34>`_)
- *Bugfix* Use ``pkg_resources`` to load registered commands (`#32 <https://github.com/pypa/twine/issues/32>`_)
- *Bugfix* Prevent ResourceWarning from being shown (`#28 <https://github.com/pypa/twine/issues/28>`_)
- *Bugfix* Add support for uploading Windows installers (`#26 <https://github.com/pypa/twine/issues/26>`_)

1.3.0 (2014-03-31)
------------------

- *Feature* Additional functionality.

1.2.2 (2013-10-03)
------------------

- *Feature* Basic functionality.
