Keyring Support
===============

Instead of typing in your password every time you upload a distribution, Twine
allows storing a username and password securely using `keyring`_.
Keyring is installed with Twine but for some systems (Linux mainly) may
require `additional installation steps`_.

Once Twine is installed, use the ``keyring`` program to set a
username and password to use for each package index (repository) to
which you may upload.

For example, to set a username and password for PyPI:

.. code-block:: bash

    keyring set https://upload.pypi.org/legacy/ your-username

or

.. code-block:: bash

    python3 -m keyring set https://upload.pypi.org/legacy/ your-username

and enter the password when prompted.

For a different repository, replace the URL with the relevant repository
URL. For example, for Test PyPI, use ``https://test.pypi.org/legacy/``.

The next time you run ``twine``, it will prompt you for a username, and then
get the appropriate password from the keyring.

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
Keyring, simply invoke:

.. code-block:: bash

    keyring --disable

or

.. code-block:: bash

    python -m keyring --disable

That command will configure for the current user the "null" keyring,
effectively disabling the functionality, and allowing Twine to prompt
for passwords.

See `twine 338 <https://github.com/pypa/twine/issues/338>`_ for
discussion and background.

.. _`keyring`: https://pypi.org/project/keyring/
.. _`Using Keyring on headless systems`:
    https://keyring.readthedocs.io/en/latest/#using-keyring-on-headless-linux-systems
.. _`additional installation steps`:
    https://pypi.org/project/keyring/#installation-linux
