:orphan:

.. See https://releases.readthedocs.io/ for instructions

=========
Changelog
=========

* :release:`3.2.0 <unreleased>`
* :feature:`666` Improve display of HTTP errors during upload
* :feature:`649` Use red text when printing errors on the command line
* :feature:`652` Print packages and signatures to be uploaded when using
  ``--verbose`` option
* :bug:`655 major` Update URL to ``.pypirc`` specfication
* :feature:`602` Require repository URL scheme to be ``http`` or ``https``
* :bug:`612 major` Don't raise an exception when Python version can't be
  parsed from filename
* :bug:`611 major` Fix inaccurate retry message during ``upload``
* :bug:`601 major` Clarify error messages for archive format
* :feature:`231` Add type annotations, checked with mypy, with :pep:`561`
  support for users of Twine's API
* :release:`3.1.1 <2019-11-27>`
* :bug:`548` Restore ``--non-interactive`` as a flag not expecting an
  argument.
* :release:`3.1.0 <2019-11-23>`
* :feature:`547` Add support for specifying ``--non-interactive`` as an
  environment variable.
* :release:`3.0.0 <2019-11-18>`
* :feature:`336` When a client certificate is indicated, all password
  processing is disabled.
* :feature:`489` Add ``--non-interactive`` flag to abort upload rather than
  interactively prompt if credentials are missing.
* :feature:`524` Twine now unconditionally requires the keyring library
  and no longer supports uninstalling ``keyring`` as a means to disable
  that functionality. Instead, use ``keyring --disable`` keyring functionality
  if necessary.
* :feature:`518` Add Python 3.8 to classifiers.
* :bug:`332 major` More robust handling of server response in
  ``--skip-existing``
* :release:`2.0.0 <2019-09-24>`
* :feature:`437` Twine now requires Python 3.6 or later. Use pip
  9 or pin to "twine<2" to install twine on older Python versions.
* :bug:`491 major` Require requests 2.20 or later to avoid reported security
  vulnerabilities in earlier releases.
* :release:`1.15.0 <2019-09-17>`
* :feature:`488` Improved output on ``check`` command:
  Prints a message when there are no distributions given to check.
  Improved handling of errors in a distribution's markup, avoiding
  messages flowing through to the next distribution's errors.
* :release:`1.14.0 <2019-09-06>`
* :feature:`456` Better error handling and gpg2 fallback if gpg not available.
* :bug:`341 major` Fail more gracefully when encountering bad metadata
* :feature:`459` Show Warehouse URL after uploading a package
* :feature:`310` Now provide a more meaningful error on redirect during upload.
* :release:`1.13.0 <2019-02-13>`
* :bug:`452 major` Restore prompts while retaining support for suppressing
  prompts.
* :bug:`447 major` Avoid requests-toolbelt to 0.9.0 to prevent attempting to
  use
  openssl when it isn't available.
* :feature:`427` Add disable_progress_bar option to disable tqdm.
* :feature:`426` Allow defining an empty username and password in .pypirc.
* :bug:`441 major` Only install pyblake2 if needed.
* :bug:`444 major` Use io.StringIO instead of StringIO.
* :bug:`436 major` Use modern Python language features.
* :support:`439` Refactor tox env and travis config.
* :bug:`435 major` Specify python_requires in setup.py
* :bug:`432 major` Use https URLs everywhere.
* :bug:`428 major` Fix --skip-existing for Nexus Repos.
* :feature:`419` Support keyring.get_credential.
* :feature:`418` Support keyring.get_username_and_password.
* :bug:`421 major` Remove unnecessary usage of readme_render.markdown.
* :feature:`416` Add Python 3.7 to classifiers.
* :bug:`412 major` Don't crash if there's no package description.
* :bug:`408 major` Fix keyring support.
* :release:`1.12.1 <2018-09-24>`
* :bug:`404` Fix regression with upload exit code
* :release:`1.12.0 <2018-09-24>`
* :feature:`395 major` Add ``twine check`` command to check long description
* :feature:`392 major` Drop support for Python 3.3
* :feature:`363` Empower ``--skip-existing`` for Artifactory repositories
* :bug:`367 major` Avoid MD5 when Python is compiled in FIPS mode
* :release:`1.11.0 <2018-03-19>`
* :bug:`269 major` Avoid uploading to PyPI when given alternate
  repository URL, and require ``http://`` or ``https://`` in
  ``repository_url``.
* :support:`277` Add instructions on how to use keyring.
* :support:`314` Add new maintainer, release checklists.
* :bug:`322 major` Raise exception if attempting upload to deprecated legacy
  PyPI URLs.
* :feature:`320` Remove PyPI as default ``register`` package index.
* :feature:`319` Support Metadata 2.1 (:pep:`566`), including Markdown
  for ``description`` fields.
* :support:`318` `Update PyPI URLs
  <https://packaging.python.org/guides/migrating-to-pypi-org/>`_.
* :release:`1.10.0 <2018-03-07>`
* :bug:`315 major` Degrade gracefully when keyring is unavailable
* :feature:`304` Reorganize & improve user & developer documentation.
* :feature:`46` Link to changelog from ``README``
* :feature:`295` Add doc building instructions
* :feature:`296` Add architecture overview to docs
* :feature:`303` Revise docs predicting future of ``twine``
* :bug:`298 major` Fix syntax highlighting in ``README``
* :bug:`299 major` Fix changelog formatting
* :bug:`200 major` Remove obsolete registration guidance
* :bug:`286 major` Fix Travis CI and test configuration
* :feature:`257` Declare support for Python 3.6
* :bug:`297 major` Fix Read the Docs, tox, Travis configuration
* :bug:`268 major` Print progress to ``stdout``, not ``stderr``
* :bug:`265 major` Fix ``--repository[-url]`` help text
* :feature:`256` Improve progressbar
* :release:`1.9.1 <2017-05-27>`
* :bug:`-` Blacklist known bad versions of Requests. See also :bug:`253`
* :release:`1.9.0 <2017-05-22>`
* :support:`-` Twine will now resolve passwords using the
  `keyring <https://pypi.org/project/keyring/>`_ if available.
  Module can be required with the ``keyring`` extra.
* :support:`-` Twine will use ``hashlib.blake2b`` on Python 3.6+
  instead of using pyblake2 for Blake2 hashes 256 bit hashes.
* :support:`-` Twine sends less information about the user's system in
  the User-Agent string. See also :bug:`229`
* :support:`-` Fix ``--skip-existing`` when used to upload a package
  for the first time.  See also :bug:`220`
* :support:`-` Fix precedence of ``--repository-url`` over
  ``--repository``. See also :bug:`206`
* :release:`1.8.1 <2016-08-09>`
* :support:`-` Check if a package exists if the URL is one of:

    * ``https://pypi.python.org/pypi/``
    * ``https://upload.pypi.org/``
    * ``https://upload.pypi.io/``

    This helps people with ``https://upload.pypi.io`` still in their
    :file:`.pypirc` file.

* :release:`1.8.0 <2016-08-08>`
* :feature:`201` Switch from upload.pypi.io to upload.pypi.org.
* :feature:`144` Retrieve configuration from the environment as a default.

    * Repository URL will default to ``TWINE_REPOSITORY``
    * Username will default to ``TWINE_USERNAME``
    * Password will default to ``TWINE_PASSWORD``

* :feature:`166` Allow the Repository URL to be provided on the
  command-line (``--repository-url``) or via an environment variable
  (``TWINE_REPOSITORY_URL``).
* :support:`-` Generate SHA256 digest for all packages
  by default.
* :feature:`171` Generate Blake2b 256 digests for packages *if* ``pyblake2``
  is installed. Users can use ``python -m pip install twine[with-blake2]``
  to have ``pyblake2`` installed with Twine.
* :support:`-` Stop testing on Python 2.6. 2.6 support will be "best
  effort" until 2.0.0
* :support:`-` Warn users if they receive a 500 error when uploading
  to ``*pypi.python.org``
* :release:`1.7.4 <2016-07-09>`
* :bug:`-` Correct a packaging error.
* :release:`1.7.3 <2016-07-08>`
* :bug:`195` Fix uploads to instances of pypiserver using
  ``--skip-existing``. We were not properly checking the return
  status code on the response after attempting an upload.
* :support:`-` Do not generate traffic to Legacy PyPI unless we're
  uploading to it or uploading to Warehouse (e.g., pypi.io). This
  avoids the attempt to upload a package to the index if we can find
  it on Legacy PyPI already.
* :release:`1.7.2 <2016-07-05>`
* :bug:`189`, :bug:`191` Fix issue where we were checking the existence of
  packages even if the user didn't specify ``--skip-existing``.
* :release:`1.7.1 <2016-07-05>`
* :bug:`187` Clint was not specified in the wheel metadata as a dependency.
* :release:`1.7.0 <2016-07-04>`
* :feature:`142` Support ``--cert`` and ``--client-cert`` command-line flags
  and config file options for feature parity with pip. This allows users to
  verify connections to servers other than PyPI (e.g., local package
  repositories) with different certificates.
* :feature:`152` Add progress bar to uploads.
* :feature:`162` Allow ``--skip-existing`` to work for 409 status codes.
* :feature:`167` Implement retries when the CDN in front of PyPI gives us a
  5xx error.
* :feature:`177` Switch Twine to upload to pypi.io instead of
  pypi.python.org.
* :bug:`186 major` Allow passwords to have ``%``\ s in them.
* :release:`1.6.5 <2015-12-16>`
* :bug:`155` Bump requests-toolbelt version to ensure we avoid
  ConnectionErrors
* :release:`1.6.4 <2015-10-27>`
* :bug:`145` Paths with hyphens in them break the Wheel regular expression.
* :bug:`146` Exception while accessing the ``repository`` key (sic)
  when raising a redirect exception.
* :release:`1.6.3 <2015-10-05>`
* :bug:`137`, :bug:`140` Uploading signatures was broken due to the pull
  request that added large file support via ``requests-toolbelt``. This
  caused a 500 error on PyPI and prevented package and signature upload in
  twine 1.6.0
* :release:`1.6.2 <2015-09-28>`
* :bug:`132` Upload signatures with packages appropriately

    As part of the refactor for the 1.6.0 release, we were using the wrong
    name to find the signature file.

    This also uncovered a bug where if you're using twine in a situation where
    ``*`` is not expanded by your shell, we might also miss uploading
    signatures to PyPI. Both were fixed as part of this.

* :release:`1.6.1 <2015-09-18>`
* :bug:`130` Fix signing support for uploads
* :release:`1.6.0 <2015-09-14>`
* :feature:`106` Upload wheels first to PyPI
* :feature:`104` Large file support via the ``requests-toolbelt``
* :bug:`92 major` Raise an exception on redirects
* :feature:`97` Allow the user to specify the location of their
  :file:`.pypirc`
* :feature:`115` Add the ``--skip-existing`` flag to ``twine upload`` to
  allow users to skip releases that already exist on PyPI.
* :bug:`114 major` Warnings triggered by pkginfo searching for
  ``PKG-INFO`` files should no longer be user visible.
* :bug:`116 major` Work around problems with Windows when using
  ``getpass.getpass``
* :bug:`111 major` Provide more helpful messages if :file:`.pypirc` is
  out of date.
* :feature:`8` Support registering new packages with ``twine register``
* :release:`1.5.0 <2015-03-10>`
* :bug:`85 major` Display information about the version of setuptools installed
* :bug:`61 major` Support deprecated pypirc file format
* :feature:`29` Support commands not named "gpg" for signing
* :support:`-` Add lower-limit to requests dependency
* :release:`1.4.0 <2014-12-12>`
* :bug:`28 major` Prevent ResourceWarning from being shown
* :bug:`34 major` List registered commands in help text
* :bug:`32 major` Use ``pkg_resources`` to load registered commands
* :bug:`47 major` Fix issue uploading packages with ``_``\ s in the name
* :bug:`26 major` Add support for uploading Windows installers
* :bug:`65 major` Expand globs and check for existence of dists to upload
* :feature:`13` Parse :file:`~/.pypirc` ourselves and use
  ``subprocess`` instead of the ``distutils.spawn`` module.
* :feature:`6` Switch to a git style dispatching for the commands to enable
  simpler commands and programmatic invocation.
* :release:`1.3.0 <2014-03-31>`
* :feature:`-` Additional functionality.
* :release:`1.2.2 <2013-10-03>`
* :feature:`0` Basic functionality.
