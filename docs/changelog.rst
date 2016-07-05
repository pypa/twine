:orphan:

=========
Changelog
=========

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

  * :bug:`186` Allow passwords to have ``%``\ s in them.

* :release:`1.6.5 <2015-12-16>`

  * :bug:`155` Bump requests-toolbelt version to ensure we avoid
    ConnectionErrors

* :release:`1.6.4 <2015-10-27>`

  * :bug:`145` Paths with hyphens in them break the Wheel regular expression.

  * :bug:`146` Exception while accessing the ``respository`` key when raising
    a redirect exception.

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

  * :bug:`92` Raise an exception on redirects

  * :feature:`97` Allow the user to specify the location of their ``.pypirc``

  * :feature:`115` Add the ``--skip-existing`` flag to ``twine upload`` to
    allow users to skip releases that already exist on PyPI.

  * :bug:`114` Warnings triggered by pkginfo searching for ``PKG-INFO`` files
    should no longer be user visible.

  * :bug:`116` Work around problems with Windows when using
    :func:`getpass.getpass`

  * :bug:`111` Provide more helpful messages if ``.pypirc`` is out of date.

  * :feature:`8` Support registering new packages with ``twine register``

* :release:`1.5.0 <2015-03-10>`

  * :bug:`85` Display information about the version of setuptools installed

  * :bug:`61` Support deprecated pypirc file format

  * :feature:`29` Support commands not named "gpg" for signing

  * Add lower-limit to requests dependency

* :release:`1.4.0 <2014-12-12>`

  * :bug:`28` Prevent ResourceWarning from being shown

  * :bug:`34` List registered commands in help text

  * :bug:`32` Use pkg_resources to load registered commands

  * :bug:`47` Fix issue uploading packages with ``_``\ s in the name

  * :bug:`26` Add support for uploading Windows installers

  * :bug:`65` Expand globs and check for existence of dists to upload

* :feature:`13` Parse ~/.pypirc ourselves and use subprocess instead of the
  distutils.spawn module.
* :feature:`6` Switch to a git style dispatching for the commands to enable
  simpler commands and programmatic invocation.
* :release:`1.2.2 <2013-10-03>`
