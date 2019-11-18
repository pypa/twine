Contributing
============

We are happy you have decided to contribute to ``twine``.

Please see `the GitHub repository`_ for code and more documentation,
and the `official Python Packaging User Guide`_ for user documentation. You can
also join ``#pypa`` or ``#pypa-dev`` `on Freenode`_, or the `pypa-dev
mailing list`_, to ask questions or get involved.

Getting started
---------------

We recommend you use a development environment. Using a ``virtualenv``
keeps your development environment isolated, so ``twine`` and its
dependencies do not interfere with other packages installed on your
machine.  You can use `virtualenv`_ or `pipenv`_ to isolate your
development environment.

Clone the twine repository from GitHub, and then make and activate a
virtual environment that uses Python 3.6 or newer as the default
Python. Example:

.. code-block:: console

  mkvirtualenv -p /usr/bin/python3.7 twine

Then, run the following command:

.. code-block:: console

  pip install -e /path/to/your/local/twine

Now, in your virtual environment, ``twine`` is pointing at your local copy, so
when you make changes, you can easily see their effect.

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Additions and edits to twine's documentation are welcome and
appreciated.

We use ``tox`` to build docs. Activate your virtual environment, then
install ``tox``.

.. code-block:: console

  pip install tox

If you are using ``pipenv`` to manage your virtual environment, you
may need the `tox-pipenv`_ plugin so that tox can use pipenv
environments instead of virtualenvs.

After making docs changes, lint and build the docs locally, using
``tox``, before making a pull request. Activate your virtual
environment, then, in the root directory, run:

.. code-block:: console

  tox -e docs

The HTML of the docs will be visible in :file:`twine/docs/_build/`.


Testing
^^^^^^^

Tests with twine are run using `tox`_, and tested against Python versions 3.6,
3.7, and 3.8. To run these tests locally, you will need to have these versions
of Python installed on your machine.

Either use ``tox`` to build against all supported Python versions (if you have
them installed) or use ``tox -e py{version}`` to test against a specific
version, e.g., ``tox -e py36`` or ``tox -e py37``.

Also, always run ``tox -e lint`` before submitting a pull request.

Submitting changes
^^^^^^^^^^^^^^^^^^

1. Fork `the GitHub repository`_.
2. Make a branch off of ``master`` and commit your changes to it.
3. Run the tests with ``tox`` and lint any docs changes with ``tox -e docs``.
4. Ensure that your name is added to the end of the :file:`AUTHORS`
   file using the format ``Name <email@domain.com> (url)``, where the
   ``(url)`` portion is optional.
5. Submit a pull request to the ``master`` branch on GitHub.


Architectural overview
----------------------

Twine is a command-line tool for interacting with PyPI securely over
HTTPS. Its three purposes are to be:

1. A user-facing tool for publishing on pypi.org
2. A user-facing tool for publishing on other Python package indexes
   (e.g., ``devpi`` instances)
3. A useful API for other programs (e.g., ``zest.releaser``) to call
   for publishing on any Python package index


Currently, twine has two principle functions: uploading new packages
and registering new `projects`_ (``register`` is no longer supported
on PyPI, and is in Twine for use with other package indexes).

Its command line arguments are parsed in :file:`twine/cli.py`. The
code for registering new projects is in
:file:`twine/commands/register.py`, and the code for uploading is in
:file:`twine/commands/upload.py`. The file :file:`twine/package.py`
contains a single class, ``PackageFile``, which hashes the project
files and extracts their metadata. The file
:file:`twine/repository.py` contains the ``Repository`` class, whose
methods control the URL the package is uploaded to (which the user can
specify either as a default, in the :file:`.pypirc` file, or pass on
the command line), and the methods that upload the package securely to
a URL.

Where Twine gets configuration and credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A user can set the repository URL, username, and/or password via
command line, ``.pypirc`` files, environment variables, and
``keyring``.


Adding a maintainer
-------------------

A checklist for adding a new maintainer to the project.

#. Add them as a Member in the GitHub repo settings. (This will also
   give them privileges on the `Travis CI project
   <https://travis-ci.org/pypa/twine>`_.)
#. Get them Test PyPI and canon PyPI usernames and add them as a
   Maintainer on `our Test PyPI project
   <https://test.pypi.org/manage/project/twine/collaboration/>`_ and
   `canon PyPI
   <https://pypi.org/manage/project/twine/collaboration/>`_.


Making a new release
--------------------

A checklist for creating, testing, and distributing a new version.

#. Choose a version number, e.g., "1.15."

#. Merge the last planned PR before the new release:

   #. Add new changes to :file:`docs/changelog.rst`.
   #. Update copyright dates.

#. Run Twine tests:

   #. ``tox -e py{36,37,38}``
   #. ``tox -e lint`` for the linter
   #. ``tox -e docs`` (this checks the Sphinx docs and uses
      ``readme_renderer`` to check that the ``long_description`` and other
      metadata will render fine on the PyPI description)

#. Create a git tag with ``git tag -sam 'Release v{number}' {number}``.

   * ``{number}``, such as ``1.15.1rc1``
   * ``-s`` signs it with your PGP key
   * ``-a`` creates an annotated tag for GitHub
   * ``-m`` adds the message; optional if you want to compose a longer
     message

#. View your tag: ``git tag -v {number}``
#. Push your tag: ``git push upstream {number}``.
#. Upload to TestPyPI with ``TWINE_REPOSITORY=https://test.pypi.org/legacy/ tox -e release``
#. Verify that everything looks good, downloads ok, etc. Make needed fixes.
#. Merge the last PR before the new release:

   #. Add new changes and new release to :file:`docs/changelog.rst`,
      with the new version ``{number}``, this time without the
      ``rc1`` suffix.

#. Run tests again. Check the changelog to verify that it looks right.
#. Create a new git tag with ``git tag -sam 'Release v{number}' {number}``.
#. View your tag: ``git tag -v {number}``
#. Push your tag: ``git push upstream {number}``.
#. On a Monday or Tuesday, upload to PyPI with ``tox -e release``.
#. Send announcement email to `pypa-dev mailing list`_ and celebrate.


Future development
------------------

See our `open issues`_.

In the future, ``pip`` and ``twine`` may
merge into a single tool; see `ongoing discussion
<https://github.com/pypa/packaging-problems/issues/60>`_.

.. _`official Python Packaging User Guide`: https://packaging.python.org/tutorials/distributing-packages/
.. _`the GitHub repository`: https://github.com/pypa/twine
.. _`on Freenode`: https://webchat.freenode.net/?channels=%23pypa-dev,pypa
.. _`pypa-dev mailing list`: https://groups.google.com/forum/#!forum/pypa-dev
.. _`virtualenv`: https://virtualenv.pypa.io/en/stable/installation/
.. _`pipenv`: https://pipenv.readthedocs.io/en/latest/
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`tox-pipenv`: https://pypi.org/project/tox-pipenv
.. _`plugin`: https://github.com/bitprophet/releases
.. _`projects`: https://packaging.python.org/glossary/#term-project
.. _`open issues`: https://github.com/pypa/twine/issues
