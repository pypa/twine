twine
=====

.. rtd-inclusion-marker-do-not-remove

Twine is `a utility`_ for `publishing`_ packages on `PyPI`_.

Currently it only supports registering `projects`_ and uploading `distributions`_.


Why Should I Use This?
----------------------

The goal of ``twine`` is to improve PyPI interaction by improving
security and testability.

The biggest reason to use ``twine`` is that it securely authenticates
you to `PyPI`_ over HTTPS using a verified connection, while ``python
setup.py upload`` `only recently stopped using HTTP
<https://bugs.python.org/issue12226>`_ in Python 2.7.9+ and Python
3.2+. This means anytime you use ``python setup.py upload`` with an
older Python version, you expose your username and password to being
easily sniffed. Twine uses only verified TLS to upload to PyPI,
protecting your credentials from theft.

Secondly, it allows you to precreate your distribution files.
``python setup.py upload`` only allows you to upload something that you've
created in the same command invocation. This means that you cannot test the
exact file you're going to upload to PyPI to ensure that it works before
uploading it.

Finally, ``twine`` allows you to pre-sign your files and pass the
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


Usage
-----

1. Create some distributions in the normal way:

   .. code-block:: console

       $ python setup.py sdist bdist_wheel

2. Upload with ``twine`` to `Test PyPI`_ and verify things look right:

   .. code-block:: console

       $ twine upload --repository-url https://test.pypi.org/legacy/ dist/*

3. Upload to `PyPI`_:

   .. code-block:: console

       $ twine upload dist/*

4. Done!

More documentation on using ``twine`` to upload packages to PyPI is in
the `Python Packaging User Guide`_.


Options
^^^^^^^

.. code-block:: console

    $ twine upload -h

    usage: twine upload [-h] [-r REPOSITORY] [--repository-url REPOSITORY_URL]
                        [-s] [--sign-with SIGN_WITH] [-i IDENTITY] [-u USERNAME]
                        [-p PASSWORD] [-c COMMENT] [--config-file CONFIG_FILE]
                        [--skip-existing] [--cert path] [--client-cert path]
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

Twine also includes a ``register`` command.

.. WARNING::
   ``register`` is `no longer necessary if you are
   uploading to pypi.org
   <https://packaging.python.org/guides/migrating-to-pypi-org/#registering-package-names-metadata>`_. As
   such, it is `no longer supported
   <https://github.com/pypa/warehouse/issues/1627>`_ in `Warehouse`_
   (the new PyPI software running on pypi.org). However, you may need
   this if you are using a different package index.

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
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file.
      --config-file CONFIG_FILE
                            The .pypirc config file to use.
      --cert path           Path to alternate CA bundle (can also be set via
                            TWINE_CERT environment variable).
      --client-cert path    Path to SSL client certificate, a single file
                            containing the private key and the certificate in PEM
                            format.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

Twine also supports configuration via environment variables. Options passed on
the command line will take precedence over options set via environment
variables. Definition via environment variable is helpful in environments where
it is not convenient to create a `.pypirc` file, such as a CI/build server, for
example.

* ``TWINE_USERNAME`` - the username to use for authentication to the repository
* ``TWINE_PASSWORD`` - the password to use for authentication to the repository
* ``TWINE_REPOSITORY`` - the repository configuration, either defined as a
  section in `.pypirc` or provided as a full URL
* ``TWINE_REPOSITORY_URL`` - the repository URL to use
* ``TWINE_CERT`` - custom CA certificate to use for repositories with
  self-signed or untrusted certificates

Resources
---------

* `IRC <http://webchat.freenode.net/?channels=%23pypa>`_
  (``#pypa`` - irc.freenode.net)
* `GitHub repository <https://github.com/pypa/twine>`_
* User and developer `documentation`_
* `Python Packaging User Guide`_

Contributing
------------

See our `developer documentation`_ for how to get started, an
architectural overview, and our future development plans.

Code of Conduct
---------------

Everyone interacting in the ``twine`` project's codebases, issue
trackers, chat rooms, and mailing lists is expected to follow the
`PyPA Code of Conduct`_.

.. _`a utility`: https://pypi.org/project/twine/
.. _`publishing`: https://packaging.python.org/tutorials/distributing-packages/
.. _`PyPI`: https://pypi.org
.. _`Test PyPI`: https://packaging.python.org/guides/using-testpypi/
.. _`Python Packaging User Guide`: https://packaging.python.org/tutorials/distributing-packages/
.. _`documentation`: https://twine.readthedocs.io/
.. _`developer documentation`: https://twine.readthedocs.io/en/latest/contributing.html
.. _`projects`: https://packaging.python.org/glossary/#term-project
.. _`distributions`: https://packaging.python.org/glossary/#term-distribution-package
.. _`PyPA Code of Conduct`: https://www.pypa.io/en/latest/code-of-conduct/
.. _`Warehouse`: https://github.com/pypa/warehouse
.. _`wheels`: https://packaging.python.org/glossary/#term-wheel
