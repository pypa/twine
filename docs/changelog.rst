:orphan:

=========
Changelog
=========

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
