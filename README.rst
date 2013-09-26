twine
=====

Twine is a utility for interacting with PyPI.

Currently it only supports uploading distributions.


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
      dist                  The distribution files to upload to the repository

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
