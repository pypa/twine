.. twine documentation master file, originally created by
    sphinx-quickstart on Tue Aug 13 11:51:54 2013.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to twine's documentation!
=================================

Twine is `a utility`_ for `publishing`_ Python packages on `PyPI`_.

It provides build system independent uploads of source and binary
`distribution artifacts <distributions_>`_ for both new and existing
`projects`_.

.. contents:: Table of Contents
    :local:

Why Should I Use This?
----------------------

The goal of Twine is to improve PyPI interaction by improving
security and testability.

The biggest reason to use Twine is that it securely authenticates
you to `PyPI`_ over HTTPS using a verified connection, regardless of
the underlying Python version. Meanwhile, ``python setup.py upload``
will only work correctly and securely if your build system, Python
version, and underlying operating system are configured properly.

Secondly, Twine encourages you to build your distribution files. ``python
setup.py upload`` only allows you to upload a package as a final step after
building with ``distutils`` or ``setuptools``, within the same command
invocation. This means that you cannot test the exact file you're going to
upload to PyPI to ensure that it works before uploading it.

Finally, Twine allows you to pre-sign your files and pass the
``.asc`` files into the command line invocation (``twine upload
myproject-1.0.1.tar.gz myproject-1.0.1.tar.gz.asc``). This enables you
to be assured that you're typing your ``gpg`` passphrase into ``gpg``
itself and not anything else, since *you* will be the one directly
executing ``gpg --detach-sign -a <filename>``.

Features
--------

- Verified HTTPS connections
- Uploading doesn't require executing ``setup.py``
- Uploading files that have already been created, allowing testing of
  distributions before release
- Supports uploading any packaging format (including `wheels`_)

Installation
------------

.. code-block:: console

    $ pip install twine

Using Twine
-----------

1. Create some distributions in the normal way:

    .. code-block:: console

       $ python setup.py sdist bdist_wheel

2. Upload with ``twine`` to `Test PyPI`_ and verify things look right.
   Twine will automatically prompt for your username and password:

    .. code-block:: console

       $ twine upload -r testpypi dist/*
       username: ...
       password:
       ...

3. Upload to `PyPI`_:

    .. code-block:: console

       $ twine upload dist/*

4. Done!

More documentation on using Twine to upload packages to PyPI is in
the `Python Packaging User Guide`_.

Commands
--------

``twine upload``
^^^^^^^^^^^^^^^^

Uploads one or more distributions to a repository.

.. code-block:: console

    $ twine upload -h
    usage: twine upload [-h] [-r REPOSITORY] [--repository-url REPOSITORY_URL]
                        [-s] [--sign-with SIGN_WITH] [-i IDENTITY] [-u USERNAME]
                        [-p PASSWORD] [-c COMMENT] [--config-file CONFIG_FILE]
                        [--skip-existing] [--cert path] [--client-cert path]
                        [--verbose] [--disable-progress-bar]
                        dist [dist ...]

    positional arguments:
      dist                  The distribution files to upload to the repository
                            (package index). Usually dist/* . May additionally
                            contain a .asc file to include an existing signature
                            with the file upload.

    optional arguments:
      -h, --help            show this help message and exit
      -r REPOSITORY, --repository REPOSITORY
                            The repository (package index) to upload the package
                            to. Should be a section in the config file (default:
                            pypi). (Can also be set via TWINE_REPOSITORY
                            environment variable.)
      --repository-url REPOSITORY_URL
                            The repository (package index) URL to upload the
                            package to. This overrides --repository. (Can also be
                            set via TWINE_REPOSITORY_URL environment variable.)
      -s, --sign            Sign files to upload using GPG.
      --sign-with SIGN_WITH
                            GPG program used to sign uploads (default: gpg).
      -i IDENTITY, --identity IDENTITY
                            GPG identity used to sign files.
      -u USERNAME, --username USERNAME
                            The username to authenticate to the repository
                            (package index) as. (Can also be set via
                            TWINE_USERNAME environment variable.)
      -p PASSWORD, --password PASSWORD
                            The password to authenticate to the repository
                            (package index) with. (Can also be set via
                            TWINE_PASSWORD environment variable.)
      --non-interactive     Do not interactively prompt for username/password
                            if the required credentials are missing. (Can also
                            be set via TWINE_NON_INTERACTIVE environment
                            variable.)
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file.
      --config-file CONFIG_FILE
                            The .pypirc config file to use.
      --skip-existing       Continue uploading files if one already exists. (Only
                            valid when uploading to PyPI. Other implementations
                            may not support this.)
      --cert path           Path to alternate CA bundle (can also be set via
                            TWINE_CERT environment variable).
      --client-cert path    Path to SSL client certificate, a single file
                            containing the private key and the certificate in PEM
                            format.
      --verbose             Show verbose output.
      --disable-progress-bar
                            Disable the progress bar.

``twine check``
^^^^^^^^^^^^^^^

Checks whether your distribution's long description will render correctly on
PyPI.

.. code-block:: console

    $ twine check -h
    usage: twine check [-h] [--strict] dist [dist ...]

    positional arguments:
      dist        The distribution files to check, usually dist/*

    optional arguments:
      -h, --help  show this help message and exit
      --strict    Fail on warnings

``twine register``
^^^^^^^^^^^^^^^^^^

**WARNING**: The ``register`` command is `no longer necessary if you are
uploading to pypi.org`_.  As such, it is `no longer supported`_ in `Warehouse`_
(the new PyPI software running on pypi.org). However, you may need this if you
are using a different package index.

For completeness, its usage:

.. code-block:: console

    $ twine register -h

    usage: twine register [-h] -r REPOSITORY [--repository-url REPOSITORY_URL]
                          [-u USERNAME] [-p PASSWORD] [-c COMMENT]
                          [--config-file CONFIG_FILE] [--cert path]
                          [--client-cert path]
                          package

    positional arguments:
      package               File from which we read the package metadata.

    optional arguments:
      -h, --help            show this help message and exit
      -r REPOSITORY, --repository REPOSITORY
                            The repository (package index) to register the package
                            to. Should be a section in the config file. (Can also
                            be set via TWINE_REPOSITORY environment variable.)
                            Initial package registration no longer necessary on
                            pypi.org:
                            https://packaging.python.org/guides/migrating-to-pypi-
                            org/
      --repository-url REPOSITORY_URL
                            The repository (package index) URL to register the
                            package to. This overrides --repository. (Can also be
                            set via TWINE_REPOSITORY_URL environment variable.)
      -u USERNAME, --username USERNAME
                            The username to authenticate to the repository
                            (package index) as. (Can also be set via
                            TWINE_USERNAME environment variable.)
      -p PASSWORD, --password PASSWORD
                            The password to authenticate to the repository
                            (package index) with. (Can also be set via
                            TWINE_PASSWORD environment variable.)
      --non-interactive     Do not interactively prompt for username/password
                            if the required credentials are missing. (Can also
                            be set via TWINE_NON_INTERACTIVE environment
                            variable.)
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file.
      --config-file CONFIG_FILE
                            The .pypirc config file to use.
      --cert path           Path to alternate CA bundle (can also be set via
                            TWINE_CERT environment variable).
      --client-cert path    Path to SSL client certificate, a single file
                            containing the private key and the certificate in PEM
                            format.

Configuration
-------------

Twine can read repository configuration from a ``.pypirc`` file, either in your
home directory, or provided with the ``--config-file`` option. For details on
writing and using ``.pypirc``, see the `specification <pypirc_>`_ in the Python
Packaging User Guide.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

Twine also supports configuration via environment variables. Options passed on
the command line will take precedence over options set via environment
variables. Definition via environment variable is helpful in environments where
it is not convenient to create a ``.pypirc`` file (for example,
on a CI/build server).

* ``TWINE_USERNAME`` - the username to use for authentication to the
  repository.
* ``TWINE_PASSWORD`` - the password to use for authentication to the
  repository.
* ``TWINE_REPOSITORY`` - the repository configuration, either defined as a
  section in ``.pypirc`` or provided as a full URL.
* ``TWINE_REPOSITORY_URL`` - the repository URL to use.
* ``TWINE_CERT`` - custom CA certificate to use for repositories with
  self-signed or untrusted certificates.
* ``TWINE_NON_INTERACTIVE`` - Do not interactively prompt for username/password
  if the required credentials are missing.

Keyring Support
---------------

Instead of typing in your password every time you upload a distribution, Twine
allows storing a username and password securely using `keyring`_.
Keyring is installed with Twine but for some systems (Linux mainly) may
require `additional installation steps`_.

Once Twine is installed, use the ``keyring`` program to set a
username and password to use for each package index (repository) to
which you may upload.

For example, to set a username and password for PyPI:

.. code-block:: console

    $ keyring set https://upload.pypi.org/legacy/ your-username

or

.. code-block:: console

    $ python3 -m keyring set https://upload.pypi.org/legacy/ your-username

and enter the password when prompted.

For a different repository, replace the URL with the relevant repository
URL. For example, for Test PyPI, use ``https://test.pypi.org/legacy/``.

The next time you run ``twine``, it will prompt you for a username and will
grab the appropriate password from the keyring.

**Note:** If you are using Linux in a headless environment (such as on a
server) you'll need to do some additional steps to ensure that Keyring can
store secrets securely. See `Using Keyring on headless systems`_.

Disabling Keyring
^^^^^^^^^^^^^^^^^

In most cases, simply not setting a password with ``keyring`` will allow Twine
to fall back to prompting for a password. In some cases, the presence of
Keyring will cause unexpected or undesirable prompts from the backing system.
In these cases, it may be desirable to disable Keyring altogether. To disable
Keyring, simply invoke:

.. code-block:: console

    $ keyring --disable

or

.. code-block:: console

    $ python -m keyring --disable

That command will configure for the current user the "null" keyring,
effectively disabling the functionality, and allowing Twine to prompt
for passwords.

See `twine 338 <https://github.com/pypa/twine/issues/338>`_ for
discussion and background.

Resources
---------

* `IRC <https://webchat.freenode.net/?channels=%23pypa>`_:
  ``#pypa`` on irc.freenode.net
* `GitHub repository <https://github.com/pypa/twine>`_
* User and developer `documentation`_
* `Python Packaging User Guide`_

Contributing
------------

See our `developer documentation`_ for how to get started, an
architectural overview, and our future development plans.

Code of Conduct
---------------

Everyone interacting in the Twine project's codebases, issue
trackers, chat rooms, and mailing lists is expected to follow the
`PSF Code of Conduct`_.

.. _`a utility`: https://pypi.org/project/twine/
.. _`publishing`: https://packaging.python.org/tutorials/distributing-packages/
.. _`PyPI`: https://pypi.org
.. _`Test PyPI`: https://packaging.python.org/guides/using-testpypi/
.. _`pypirc`: https://packaging.python.org/specifications/pypirc/
.. _`Python Packaging User Guide`:
    https://packaging.python.org/tutorials/distributing-packages/
.. _`keyring`: https://pypi.org/project/keyring/
.. _`Using Keyring on headless systems`:
    https://keyring.readthedocs.io/en/latest/#using-keyring-on-headless-linux-systems
.. _`additional installation steps`:
    https://pypi.org/project/keyring/#installation-linux
.. _`documentation`: https://twine.readthedocs.io/
.. _`developer documentation`:
    https://twine.readthedocs.io/en/latest/contributing.html
.. _`projects`: https://packaging.python.org/glossary/#term-Project
.. _`distributions`:
    https://packaging.python.org/glossary/#term-Distribution-Package
.. _`PSF Code of Conduct`: https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md
.. _`Warehouse`: https://github.com/pypa/warehouse
.. _`wheels`: https://packaging.python.org/glossary/#term-Wheel
.. _`no longer necessary if you are uploading to pypi.org`:
    https://packaging.python.org/guides/migrating-to-pypi-org/#registering-package-names-metadata
.. _`no longer supported`: https://github.com/pypa/warehouse/issues/1627

.. toctree::
    :caption: Further documentation
    :maxdepth: 3

    contributing
    changelog
    Python Packaging User Guide <https://packaging.python.org/tutorials/distributing-packages/>

* :ref:`search`
