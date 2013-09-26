twine
=====

Twine is a utility for interacting with PyPI.

Currently it only supports uploading distributions.


Why Should I Use This?
----------------------

The biggest reason to use twine is that ``python setup.py upload`` uploads
files over plaintext. This means anytime you use it you expose your username
and password to a MITM attack. Twine uses only verified TLS to upload to PyPI
protecting your credentials from theft.

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

* Verified HTTPS Connections
* Uploading doesn't require executing setup.py
* Uploading files that have already been created, allowing testing of
  distributions before release


Installation
------------

.. code:: bash

    $ pip install twine


Usage
-----

1. Create some distributions in the normal way:

.. code:: bash

    $ python setup.py sdist bdist_wheel

2. Upload with twine:

.. code:: bash

    $ twine upload dist/*

3. Done!


Options
~~~~~~~

.. code:: bash

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


Resources
---------

* `IRC <http://webchat.freenode.net?channels=%23warehouse>`_
  (#warehouse - irc.freenode.net)
* `Repository <https://github.com/dstufft/twine>`_


Contributing
------------

1. Fork the `repository`_ on GitHub.
2. Make a branch off of master and commit your changes to it.
3. Ensure that your name is added to the end of the AUTHORS file using the
   format ``Name <email@domain.com> (url)``, where the ``(url)`` portion is
   optional.
4. Submit a Pull Request to the master branch on GitHub.

.. _repository: https://github.com/dstufft/twine
