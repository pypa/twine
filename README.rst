twine
=====

Twine is a utility for interacting `with PyPI <https://pypi.python.org/pypi/twine>`_.

Currently it only supports uploading distributions.


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

2. Upload with twine:

.. code-block:: bash

    $ twine upload dist/*

3. Done!


Options
~~~~~~~

.. code-block:: bash

    $ twine upload -h
    usage: twine upload [-h] [-r REPOSITORY] [-s] [-i IDENTITY] [-u USERNAME]
                        [-p PASSWORD] [-c COMMENT]
                        dist [dist ...]

    positional arguments:
      dist                  The distribution files to upload to the repository,
                            may additionally contain a .asc file to include an
                            existing signature with the file upload

    optional arguments:
      -h, --help            show this help message and exit
      -r REPOSITORY, --repository REPOSITORY
                            The repository to upload the files to
      -s, --sign            Sign files to upload using gpg
      -i IDENTITY, --identity IDENTITY
                            GPG identity used to sign files
      -u USERNAME, --username USERNAME
                            The username to authenticate to the repository as
      -p PASSWORD, --password PASSWORD
                            The password to authenticate to the repository with
      -c COMMENT, --comment COMMENT
                            The comment to include with the distribution file
      --config-file FILE    
                            The .pypirc config file to use

Note that on top of .pypirc config file you also can define repositories
to be used with twine using environment variables using following format:

..

    PYPI_REPO_<REPO_NAME>=URL

For example following environment variables:

..

    PYPI_REPO_INTERNAL_STORE=https://john:secret@pypi.local:42/stuff
    PYPI_REPO_ADDITIONAL=https://john:@pypi.additional
    PYPI_REPO_ONE_MORE=https://john@pypi.more
    PYPI_REPO_PYPI=https://pypi.external

define:

* a repository called 'internal-store' (repository names are normalized
  to lowercase and '_' replaced with '-') that will be accessed with username
  'john' and password 'secret'.

* a repository called 'additional' that will be accessed with username 'john'
  and **with empty password**

* a repository called 'one-more' that will be accessed with username 'john'
  and password will be asked during runtime

* override url for the 'default' repository called 'pypi'

With such environment you can specify any of 'internal-store', 'additional',
'one-more' and 'pypi' in -r/--repository parameter.

Resources
---------

* `IRC <http://webchat.freenode.net?channels=%23pypa>`_
  (``#pypa`` - irc.freenode.net)
* `GitHub repository <https://github.com/pypa/twine>`_


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
