.. twine documentation master file, originally created by
    sphinx-quickstart on Tue Aug 13 11:51:54 2013.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

.. toctree::
    :hidden:
    :maxdepth: 3

    keyring-support
    changelog
    contributing
    Code of Conduct <https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md>
    PyPI Project <https://pypi.org/project/twine/>
    GitHub Repository <https://github.com/pypa/twine>
    Python Packaging Tutorial <https://packaging.python.org/tutorials/distributing-packages/>

Twine
=====

Twine is a utility for `publishing`_ Python packages on `PyPI`_.
It provides build system independent uploads of source and binary
`distribution artifacts <distributions_>`_ for both new and existing
`projects`_.

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

.. code-block:: bash

    pip install twine

Using Twine
-----------

1. Create some distributions in the normal way:

   .. code-block:: bash

       python setup.py sdist bdist_wheel

2. Upload to `Test PyPI`_ and verify things look right:

   .. code-block:: bash

       twine upload -r testpypi dist/*

   Twine will prompt for your username and password.

3. Upload to `PyPI`_:

   .. code-block:: bash

       twine upload dist/*

4. Done!

More documentation on using Twine to upload packages to PyPI is in
the `Python Packaging User Guide`_.

Commands
--------

``twine upload``
^^^^^^^^^^^^^^^^

Uploads one or more distributions to a repository.

.. program-output:: twine upload -h

``twine check``
^^^^^^^^^^^^^^^

Checks whether your distribution's long description will render correctly on
PyPI.

.. program-output:: twine check -h

``twine register``
^^^^^^^^^^^^^^^^^^

.. warning::

   The ``register`` command is `no longer necessary if you are
   uploading to pypi.org`_.  As such, it is `not supported by Warehouse`_
   (the software running on pypi.org). However, you may need it if you
   are using a different package index.

For completeness, its usage:

.. program-output:: twine register -h

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

.. _`publishing`: https://packaging.python.org/tutorials/distributing-packages/
.. _`PyPI`: https://pypi.org
.. _`Test PyPI`: https://packaging.python.org/guides/using-testpypi/
.. _`pypirc`: https://packaging.python.org/specifications/pypirc/
.. _`Python Packaging User Guide`:
    https://packaging.python.org/tutorials/distributing-packages/
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
