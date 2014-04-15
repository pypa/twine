.. twine documentation master file, created by
   sphinx-quickstart on Tue Aug 13 11:51:54 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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
* Supports uploading any packaging format (including wheels).

Installation
------------

Installing twine is easy, just use `pip <http://www.pip-installer.org/en/latest/>`_.

.. code-block:: text

   $ pip install twine


PyPI Configuration
------------------

To upload a package with Twine you will need to either create a ``.pypirc`` config in your home folder or supply Twine with
your PyPI repository and user credentials. If you do not wish to store your password on disk you can alternatively
leave your password blank and Twine will prompt you for your password information before uploading your files.

The ``.pypirc`` config looks like this.

.. code-block:: ini

   [pypi]
   repository: https://pypi.python.org
   username: <username>
   password: <password>


Alternatively you can supply the necessary pypi information through commandline arguments. You can find all the
upload commandline options by viewing the upload commands help text.

.. code-block:: text

    $ twine upload -h

Usage
-----

1. Create some distributions in the normal way:

.. code:: bash

    $ python setup.py sdist bdist_wheel

2. Upload with twine:

.. code:: bash

    $ twine upload dist/*

3. Done!
