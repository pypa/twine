twine
=====

Twine is a utility for interacting `with PyPI <https://pypi.python.org/pypi/twine>`_.

Currently it only supports registering projects and uploading distributions.


Why Should I Use This?
----------------------

The biggest reason to use twine is that it securely authenticates you to PyPI
over HTTPS using a verified connection while ``python setup.py upload`` `only
recently stopped using HTTP <http://bugs.python.org/issue12226>`_ in Python
2.7.9+ and Python 3.2+. This means anytime you use ``python setup.py upload``
with an older Python version, you expose your username and password to being
easily sniffed. Twine uses only verified TLS to upload to PyPI protecting your
credentials from theft.

Secondly it allows you to precreate your distribution files.
``python setup.py upload`` only allows you to upload something that you've
created in the same command invocation. This means that you cannot test the
exact file you're going to upload to PyPI to ensure that it works before
uploading it.

Finally it allows you to pre-sign your files and pass the .asc files into
the command line invocation
(``twine upload twine-1.0.1.tar.gz twine-1.0.1.tar.gz.asc``). This enables you
to be assured that you're typing your gpg passphrase into gpg itself and not
anything else since *you* will be the one directly executing
``gpg --detach-sign -a <filename>``.


Features
--------

- Verified HTTPS Connections
- Uploading doesn't require executing setup.py
- Uploading files that have already been created, allowing testing of
  distributions before release
- Supports uploading any packaging format (including wheels).


Installation
------------

.. code-block:: bash

    $ pip install twine


Usage
-----

1. Create some distributions in the normal way:

   .. code-block:: bash

       $ python setup.py sdist bdist_wheel

2. Register your project (if necessary):

   .. code-block:: bash

       $ # One needs to be explicit here, globbing dist/* would fail.
       $ twine register dist/project_name-x.y.z.tar.gz
       $ twine register dist/mypkg-0.1-py2.py3-none-any.whl

3. Upload with twine [#]_:

   .. code-block:: bash

       $ twine upload dist/*

   .. [#] If you see the following error while uploading to PyPI, it probably means you need to register (see step 2)::

             $ HTTPError: 403 Client Error: You are not allowed to edit 'xyz' package information

4. Done!


Options for register
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ twine register -h

    usage: twine register [-h] [-r REPOSITORY] [--repository-url REPOSITORY_URL]
                          [-u USERNAME] [-p PASSWORD] [-c COMMENT]
                          [--config-file CONFIG_FILE] [--cert path]
                          [--client-cert path]
                          package

    positional arguments:
      package               File from which we read the package metadata

    optional arguments:
      -h, --help            show this help message and exit
      -r REPOSITORY, --repository REPOSITORY
                            The repository to register the package to. Can be a
                            section in the config file or a full URL to the
                            repository (default: pypi). (Can also be set via
                            TWINE_REPOSITORY environment variable)
      --repository-url REPOSITORY_URL
                            The repository URL to upload the package to. This can
                            be specified with --repository because it will be used
                            if there is no configuration for the value passed to
                            --repository. (Can also be set via
                            TWINE_REPOSITORY_URL environment variable.)
      -u USERNAME, --username USERNAME
                            The username to authenticate to the repository as (can
                            also be set via TWINE_USERNAME environment variable)
      -p PASSWORD, --password PASSWORD
                            The password to authenticate to the repository with
                            (can also be set via TWINE_PASSWORD environment
                            variable)
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file
      --config-file CONFIG_FILE
                            The .pypirc config file to use
      --cert path           Path to alternate CA bundle
      --client-cert path    Path to SSL client certificate, a single file
                            containing the private key and the certificate in PEM
                            format


Options for upload
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ twine upload -h

    usage: twine upload [-h] [-r REPOSITORY] [--repository-url REPOSITORY_URL]
                        [-s] [--sign-with SIGN_WITH] [-i IDENTITY] [-u USERNAME]
                        [-p PASSWORD] [-c COMMENT] [--config-file CONFIG_FILE]
                        [--skip-existing] [--cert path] [--client-cert path]
                        dist [dist ...]

    positional arguments:
      dist                  The distribution files to upload to the repository,
                            may additionally contain a .asc file to include an
                            existing signature with the file upload

    optional arguments:
      -h, --help            show this help message and exit
      -r REPOSITORY, --repository REPOSITORY
                            The repository to register the package to. Can be a
                            section in the config file or a full URL to the
                            repository (default: pypi). (Can also be set via
                            TWINE_REPOSITORY environment variable)
      --repository-url REPOSITORY_URL
                            The repository URL to upload the package to. This can
                            be specified with --repository because it will be used
                            if there is no configuration for the value passed to
                            --repository. (Can also be set via
                            TWINE_REPOSITORY_URL environment variable.)
      -s, --sign            Sign files to upload using gpg
      --sign-with SIGN_WITH
                            GPG program used to sign uploads (default: gpg)
      -i IDENTITY, --identity IDENTITY
                            GPG identity used to sign files
      -u USERNAME, --username USERNAME
                            The username to authenticate to the repository as (can
                            also be set via TWINE_USERNAME environment variable)
      -p PASSWORD, --password PASSWORD
                            The password to authenticate to the repository with
                            (can also be set via TWINE_PASSWORD environment
                            variable)
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file
      --config-file CONFIG_FILE
                            The .pypirc config file to use
      --skip-existing       Continue uploading files if one already exists. (Only
                            valid when uploading to PyPI. Other implementations
                            may not support this.)
      --cert path           Path to alternate CA bundle
      --client-cert path    Path to SSL client certificate, a single file
                            containing the private key and the certificate in PEM
                            format


API
---

``twine`` is written in Python.  Of course.  So if you work on a
Python tool that uses ``twine`` for uploading or registering, you can
import it.

Note that reading environment variables, for example
``TWINE_REPOSITORY``, is a feature of the command line tool.  the API
does not try to read this.


API package
~~~~~~~~~~~

Create a package object:

.. code-block:: python

    from twine.package import PackageFile
    package = PackageFile.from_filename(filename, comment)

Here ``filename`` is the name of a distribution (usually a wheel or a
source distribution) and comment is a comment to include with the
distribution file.  The comment may be ``None``.

You can add a gpg signature:

.. code-block:: python

    package.add_gpg_signature(signature_filepath, signature_filename)

You can sign a package:

.. code-block:: python

    package.sign(sign_with, identity)


API repository
~~~~~~~~~~~~~~

Define a repository:

.. code-block:: python

    from twine.repository import Repository
    repository = Repository(config["repository"], username, password)
    repository.set_certificate_authority(ca_cert)
    repository.set_client_certificate(client_cert)


Register a package:

.. code-block:: python

    package = PackageFile.from_filename(filename, comment)
    response = repository.register()

Upload a package:

.. code-block:: python

    if repository.package_is_uploaded(package):
        ...
    response = repository.upload(package)
    repository.close()


API exceptions
~~~~~~~~~~~~~~

When things go wrong:

.. code-block:: python

    # A redirect was detected that the user needs to resolve.
    from twine.exceptions import RedirectDetected

    # A package file was provided that could not be found on the file system.
    from twine.exceptions import PackageNotFound


API register
~~~~~~~~~~~~

Since version 2.0 you can use this:

.. code-block:: python

    from twine.commands.register import register
    upload('dist/mypkg-0.1-py2.py3-none-any.whl')

It takes as only required argument the name of a file from which we
read the package metadata.  This is usually a wheel or a source
distribution.

You can pass several optional keyword arguments.  This is the list,
including the default values:

.. code-block:: python

   repository="pypi",
   username=None,
   password=None,
   comment=None,
   config_file="~/.pypirc",
   cert=None,
   client_cert=None,
   repository_url=None,


API upload
~~~~~~~~~~

Since version 2.0 you can use this:

.. code-block:: python

    from twine.commands.upload import upload
    upload(['dist/project_name-x.y.z.tar.gz', 'dist/mypkg-0.1-py2.py3-none-any.whl'])

Only a list of files to upload is required.  You can pass several
optional keyword arguments.  This is the list, including the default
values:

.. code-block:: python

        repository="pypi",
        sign=False,
        identity=None,
        username=None,
        password=None,
        comment=None,
        sign_with="gpg",
        config_file="~/.pypirc",
        skip_existing=False,
        cert=None,
        client_cert=None,
        repository_url=None,


Resources
---------

* `IRC <http://webchat.freenode.net?channels=%23pypa>`_
  (``#pypa`` - irc.freenode.net)
* `GitHub repository <https://github.com/pypa/twine>`_
* `Python Packaging User Guide <https://packaging.python.org/en/latest/distributing/>`_

Contributing
------------

1. Fork the `repository <https://github.com/pypa/twine>`_ on GitHub.
2. Make a branch off of master and commit your changes to it.
3. Run the tests with ``tox``

   - Either use ``tox`` to build against all supported Python versions (if you
     have them installed) or use ``tox -e py{version}`` to test against a
     specific version, e.g., ``tox -e py27`` or ``tox -e py34``.
   - Always run ``tox -e pep8``

4. Ensure that your name is added to the end of the AUTHORS file using the
   format ``Name <email@domain.com> (url)``, where the ``(url)`` portion is
   optional.
5. Submit a Pull Request to the master branch on GitHub.

If you'd like to have a development environment for twine, you should create a
virtualenv and then do ``pip install -e .`` from within the directory.


Code of Conduct
---------------

Everyone interacting in the twine project's codebases, issue trackers, chat
rooms, and mailing lists is expected to follow the `PyPA Code of Conduct`_.

.. _PyPA Code of Conduct: https://www.pypa.io/en/latest/code-of-conduct/
