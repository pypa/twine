Contributing
============

We are happy you have decided to contribute to twine.

Please see `the GitHub repository`_ for code and more documentation,
and the `official Python Packaging User Guide`_ for user documentation. You can
also join ``#pypa`` or ``#pypa-dev`` `on Freenode`_, or the `distutils-sig
mailing list`_, to ask questions or get involved.

Getting started
---------------

We recommend you use a `virtual environment`_, so that twine and its
dependencies do not interfere with other packages installed on your
machine.

Clone the twine repository from GitHub, then make and activate a
virtual environment that uses Python 3.6 or newer as the default
Python. For example:

.. code-block:: console

    cd /path/to/your/local/twine
    python3.6 -m venv venv
    source venv/bin/activate

Then, run the following command:

.. code-block:: console

    pip install -e .

Now, in your virtual environment, ``twine`` is pointing at your local copy, so
when you make changes, you can easily see their effect.

We use `tox`_ to run tests, check code style, and build the documentation.
To install ``tox`` in your active virtual environment, run:

.. code-block:: console

    pip install tox

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Additions and edits to twine's documentation are welcome and
appreciated.

To preview the docs while you're making changes, run:

.. code-block:: console

    tox -e watch-docs

Then open a web browser to `<http://127.0.0.1:8000>`_.

When you're done making changes, lint and build the docs locally before making
a pull request. In your active virtual environment, run:

.. code-block:: console

    tox -e docs

The HTML of the docs will be written to :file:`docs/_build/html`.

Code style
^^^^^^^^^^

To automatically reformat your changes with `isort`_ and `black`_, run:

.. code-block:: console

    tox -e format

To detect any remaining code smells with `flake8`_, run:

.. code-block:: console

    tox -e lint

To perform strict type-checking using `mypy`_, run:

.. code-block:: console

    tox -e types

Any errors from ``lint`` or ``types`` need to be fixed manually.

Additionally, we prefer that ``import`` statements be used for packages and
modules only, rather than individual classes or functions.

Testing
^^^^^^^

We use `pytest`_ for writing and running tests.

To run the tests in your virtual environment, run:

.. code-block:: console

    tox -e py

To pass options to ``pytest``, e.g. the name of a test, run:

.. code-block:: console

    tox -e py -- tests/test_upload.py::test_exception_for_http_status

Twine is continuously tested against Python 3.6, 3.7, 3.8, and 3.9 using
`GitHub Actions`_. To run the tests against a specific version, e.g. Python
3.6, you will need it installed on your machine. Then, run:

.. code-block:: console

    tox -e py36

To run the "integration" tests of uploading to real package indexes, run:

.. code-block:: console

    tox -e integration

To run the tests against all supported Python versions, check code style,
and build the documentation, run:

.. code-block:: console

    tox


Submitting changes
^^^^^^^^^^^^^^^^^^

1. Fork `the GitHub repository`_.
2. Make a branch off of ``master`` and commit your changes to it.
3. Run the tests, check code style, and build the docs as described above.
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

#. Add them as a Member in the GitHub repo settings.
#. Get them Test PyPI and canon PyPI usernames and add them as a
   Maintainer on `our Test PyPI project
   <https://test.pypi.org/manage/project/twine/collaboration/>`_ and
   `canon PyPI
   <https://pypi.org/manage/project/twine/collaboration/>`_.


Making a new release
--------------------

A checklist for creating, testing, and distributing a new version.

#. Add user-facing changes to :file:`docs/changelog.rst`.
#. Choose a version number, e.g. ``3.2.0``.
#. Add a ``:release:`` line to :file:`docs/changelog.rst`.
#. Commit and open a pull request for review.
#. Merge the pull request, and ensure the `GitHub Actions`_ build passes.
#. Create a new git tag with ``git tag -m "Release v{version}" {version}``.
#. Push the new tag with ``git push upstream {version}``.
#. Watch the release in `Travis`_.
#. Send announcement email to `distutils-sig mailing list`_ and celebrate.


Future development
------------------

See our `open issues`_.

In the future, ``pip`` and ``twine`` may
merge into a single tool; see `ongoing discussion
<https://github.com/pypa/packaging-problems/issues/60>`_.

.. _`official Python Packaging User Guide`: https://packaging.python.org/tutorials/distributing-packages/
.. _`the GitHub repository`: https://github.com/pypa/twine
.. _`on Freenode`: https://webchat.freenode.net/?channels=%23pypa-dev,pypa
.. _`distutils-sig mailing list`: https://mail.python.org/mailman3/lists/distutils-sig.python.org/
.. _`virtual environment`: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
.. _`tox`: https://tox.readthedocs.io/
.. _`pytest`: https://docs.pytest.org/
.. _`GitHub Actions`: https://github.com/pypa/twine/actions
.. _`Travis`: https://travis-ci.com/github/pypa/twine
.. _`isort`: https://timothycrosley.github.io/isort/
.. _`black`: https://black.readthedocs.io/
.. _`flake8`: https://flake8.pycqa.org/
.. _`mypy`: https://mypy.readthedocs.io/
.. _`plugin`: https://github.com/bitprophet/releases
.. _`projects`: https://packaging.python.org/glossary/#term-Project
.. _`open issues`: https://github.com/pypa/twine/issues
