.. twine documentation master file, originally created by
   sphinx-quickstart on Tue Aug 13 11:51:54 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :hidden:
   :maxdepth: 3

   changelog
   contributing
   Code of Conduct <https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md>
   PyPI Project <https://pypi.org/project/twine/>
   GitHub Repository <https://github.com/pypa/twine>
   Python Packaging Tutorial <https://packaging.python.org/tutorials/packaging-projects/>

Twine
=====

Twine is a utility for `publishing`_ Python packages to `PyPI`_ and other
`repositories`_. It provides build system independent uploads of source and
binary `distribution artifacts <distributions_>`_ for both new and existing
`projects`_.

Why Should I Use This?
----------------------

The goal of Twine is to improve PyPI interaction by improving
security and testability.

The biggest reason to use Twine is that it securely authenticates
you to PyPI over HTTPS using a verified connection, regardless of
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

      python -m build

2. Upload to `Test PyPI`_ and verify things look right:

   .. code-block:: bash

      twine upload -r testpypi dist/*

   Twine will prompt for your username and password.

3. Upload to `PyPI`_:

   .. code-block:: bash

      twine upload dist/*

4. Done!

.. _entering-credentials:

.. note::

   Like many other command line tools, Twine does not show any characters when
   you enter your password.

   If you're using Windows and trying to paste your username, password, or
   token in the Command Prompt or PowerShell, ``Ctrl-V`` and ``Shift+Insert``
   won't work. Instead, you can use "Edit > Paste" from the window menu, or
   enable "Use Ctrl+Shift+C/V as Copy/Paste" in "Properties". This is a
   `known issue <https://bugs.python.org/issue37426>`_ with Python's
   ``getpass`` module.

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

Pre-register a name with a repository before uploading a distribution.

.. warning::

   Pre-registration is `not supported on PyPI`_, so the ``register`` command is
   only necessary if you are using a different repository that requires it. See
   `issue #1627 on Warehouse`_ (the software running on PyPI) for more details.

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

Proxy Support
^^^^^^^^^^^^^

Twine can be configured to use a proxy by setting environment variables.
For example, to use a proxy for just the ``twine`` command,
without ``export``-ing it for other tools:

.. code-block:: bash

   HTTPS_PROXY=socks5://user:pass@host:port twine upload dist/*

For more information, see the Requests documentation on
:ref:`requests:proxies` and :ref:`requests:socks`, and
`an in-depth article about proxy environment variables
<https://about.gitlab.com/blog/2021/01/27/we-need-to-talk-no-proxy/>`_.

Keyring Support
---------------

Instead of typing in your password every time you upload a distribution, Twine
allows storing a username and password securely using `keyring`_.
Keyring is installed with Twine but for some systems (Linux mainly) may
require `additional installation steps`_.

Once Twine is installed, use the ``keyring`` program to set a username and
password to use for each repository to which you may upload.

For example, to set a username and password for PyPI:

.. code-block:: bash

   keyring set https://upload.pypi.org/legacy/ your-username

and enter the password when prompted.

For a different repository, replace the URL with the relevant repository
URL. For example, for Test PyPI, use ``https://test.pypi.org/legacy/``.

The next time you run ``twine``, it will prompt you for a username, and then
get the appropriate password from Keyring.

.. note::

   If you are using Linux in a headless environment (such as on a
   server) you'll need to do some additional steps to ensure that Keyring can
   store secrets securely. See `Using Keyring on headless systems`_.

Disabling Keyring
^^^^^^^^^^^^^^^^^

In most cases, simply not setting a password with ``keyring`` will allow Twine
to fall back to prompting for a password. In some cases, the presence of
Keyring will cause unexpected or undesirable prompts from the backing system.
In these cases, it may be desirable to disable Keyring altogether. To disable
Keyring, run:

.. code-block:: bash

   keyring --disable

See `Twine issue #338`_ for discussion and background.


.. _`publishing`: https://packaging.python.org/tutorials/packaging-projects/
.. _`PyPI`: https://pypi.org
.. _`Test PyPI`: https://packaging.python.org/guides/using-testpypi/
.. _`pypirc`: https://packaging.python.org/specifications/pypirc/
.. _`Python Packaging User Guide`:
   https://packaging.python.org/tutorials/packaging-projects/
.. _`keyring`: https://pypi.org/project/keyring/
.. _`Using Keyring on headless systems`:
   https://keyring.readthedocs.io/en/latest/#using-keyring-on-headless-linux-systems
.. _`additional installation steps`:
   https://pypi.org/project/keyring/#installation-linux
.. _`developer documentation`:
   https://twine.readthedocs.io/en/latest/contributing.html
.. _`projects`: https://packaging.python.org/glossary/#term-Project
.. _`distributions`:
   https://packaging.python.org/glossary/#term-Distribution-Package
.. _`repositories`:
   https://packaging.python.org/glossary/#term-Package-Index
.. _`PSF Code of Conduct`: https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md
.. _`Warehouse`: https://github.com/pypa/warehouse
.. _`wheels`: https://packaging.python.org/glossary/#term-Wheel
.. _`not supported on PyPI`:
   https://packaging.python.org/guides/migrating-to-pypi-org/#registering-package-names-metadata
.. _`issue #1627 on Warehouse`: https://github.com/pypa/warehouse/issues/1627
.. _`Twine issue #338`: https://github.com/pypa/twine/issues/338
