Contributing
============

We are happy you have decided to contribute to Twine.

Please see `the GitHub repository`_ for code and more documentation,
and the `official Python Packaging User Guide`_ for user documentation.
To ask questions or get involved, you can join the `Python Packaging
Discourse forum`_, ``#pypa`` or ``#pypa-dev`` on `IRC`_, or the
`distutils-sig mailing list`_.

Everyone interacting in the Twine project's codebases, issue
trackers, chat rooms, and mailing lists is expected to follow the
`PSF Code of Conduct`_.

Getting started
---------------

We use `tox`_ to run tests, check code style, and build the documentation.
To install ``tox``, run:

.. code-block:: bash

   python3 -m pip install tox

Clone the twine repository from GitHub, then run:

.. code-block:: bash

   cd /path/to/your/local/twine
   tox -e dev

This creates a `virtual environment`_, so that twine and its
dependencies do not interfere with other packages installed on your
machine. In the virtual environment, ``twine`` is pointing at your
local copy, so when you make changes, you can easily see their effect.

The virtual environment also contains the tools for running tests
and checking code style, so you can run them on single files directly or
in your code editor. However, we still encourage using the ``tox`` commands
below on the whole codebase.

To use the virtual environment, run:

.. code-block:: bash

   source venv/bin/activate

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Additions and edits to twine's documentation are welcome and
appreciated.

To preview the docs while you're making changes, run:

.. code-block:: bash

   tox -e watch-docs

Then open a web browser to `<http://127.0.0.1:8000>`_.

When you're done making changes, lint and build the docs locally before making
a pull request. In your active virtual environment, run:

.. code-block:: bash

   tox -e docs

The HTML of the docs will be written to :file:`docs/_build/html`.

Code style
^^^^^^^^^^

To automatically reformat your changes with `isort`_ and `black`_, run:

.. code-block:: bash

   tox -e format

To detect any remaining code smells with `flake8`_, run:

.. code-block:: bash

   tox -e lint

To perform strict type-checking using `mypy`_, run:

.. code-block:: bash

   tox -e types

Any errors from ``lint`` or ``types`` need to be fixed manually.

Additionally, we prefer that ``import`` statements be used for packages and
modules only, rather than individual classes or functions.

Testing
^^^^^^^

We use `pytest`_ for writing and running tests.

To run the tests in your virtual environment, run:

.. code-block:: bash

   tox -e py

To pass options to ``pytest``, e.g. the name of a test, run:

.. code-block:: bash

   tox -e py -- tests/test_upload.py::test_exception_for_http_status

Twine is continuously tested against Python 3.6, 3.7, 3.8, and 3.9 using
`GitHub Actions`_. To run the tests against a specific version, e.g. Python
3.6, you will need it installed on your machine. Then, run:

.. code-block:: bash

   tox -e py36

To run the "integration" tests of uploading to real package indexes, run:

.. code-block:: bash

   tox -e integration

To run the tests against all supported Python versions, check code style,
and build the documentation, run:

.. code-block:: bash

   tox


Submitting changes
------------------

1. Fork `the GitHub repository`_.
2. Make a branch off of ``main`` and commit your changes to it.
3. Run the tests, check code style, and build the docs as described above.
4. Optionally, add your name to the end of the :file:`AUTHORS`
   file using the format ``Name <email@domain.com> (url)``, where the
   ``(url)`` portion is optional.
5. Submit a pull request to the ``main`` branch on GitHub, referencing an
   open issue.
6. Add a changelog entry.

Changelog entries
^^^^^^^^^^^^^^^^^

The ``docs/changelog.rst`` file is built by `towncrier`_ from files in the
``changelog/`` directory. To add an entry, create a file in that directory
named ``{number}.{type}.rst``, where ``{number}`` is the pull request number,
and ``{type}`` is ``feature``, ``bugfix``, ``doc``, ``removal``, or ``misc``.

For example, if your PR number is 1234 and it's fixing a bug, then you
would create ``changelog/1234.bugfix.rst``. PRs can span multiple categories by
creating multiple files: if you added a feature and deprecated/removed an old
feature in PR #5678, you would create ``changelog/5678.feature.rst`` and
``changelog/5678.removal.rst``.

A changelog entry is meant for end users and should only contain details
relevant to them. In order to maintain a consistent style, please keep the
entry to the point, in sentence case, shorter than 80 characters, and in an
imperative tone. An entry should complete the sentence "This change will ...".
If one line is not enough, use a summary line in an imperative tone, followed
by a description of the change in one or more paragraphs, each wrapped at 80
characters and separated by blank lines.

You don't need to reference the pull request or issue number in a changelog
entry, since towncrier will add a link using the number in the file name,
and the pull request should reference an issue number. Similarly, you don't
need to add your name to the entry, since that will be associated with the pull
request.

Changelog entries are rendered using `reStructuredText`_, but they should only
have minimal formatting (such as ````monospaced text````).

.. _`towncrier`: https://pypi.org/project/towncrier/
.. _`reStructuredText`: https://www.writethedocs.org/guide/writing/reStructuredText/


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

For more details, refer to the source documentation (currently a
`work in progress <https://github.com/pypa/twine/issues/635>`_):

.. toctree::

   internal/twine

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

#. Choose a version number, and create a new branch

   .. code-block:: bash

      VERSION=3.4.2

      git switch -c release-$VERSION

#. Update :file:`docs/changelog.rst`

   .. code-block:: bash

      tox -e changelog -- --version $VERSION

      git commit -am "Update changelog for $VERSION"

#. Open a pull request for review

#. Merge the pull request, and ensure the `GitHub Actions`_ build passes

#. Create a new git tag for the version

   .. code-block:: bash

      git switch main

      git pull --ff-only upstream main

      git tag -m "Release v$VERSION" $VERSION

#. Push to start the release, and watch it in `GitHub Actions`_

   .. code-block:: bash

      git push upstream $VERSION

#. View the new release on `PyPI`_

Future development
------------------

See our `open issues`_.

In the future, ``pip`` and ``twine`` may
merge into a single tool; see `ongoing discussion
<https://github.com/pypa/packaging-problems/issues/60>`_.

.. _`official Python Packaging User Guide`: https://packaging.python.org/tutorials/distributing-packages/
.. _`the GitHub repository`: https://github.com/pypa/twine
.. _`Python Packaging Discourse forum`: https://discuss.python.org/c/packaging/
.. _`IRC`: https://web.libera.chat/#pypa-dev,#pypa
.. _`distutils-sig mailing list`: https://mail.python.org/mailman3/lists/distutils-sig.python.org/
.. _`PSF Code of Conduct`: https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md
.. _`virtual environment`: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
.. _`tox`: https://tox.readthedocs.io/
.. _`pytest`: https://docs.pytest.org/
.. _`GitHub Actions`: https://github.com/pypa/twine/actions
.. _`isort`: https://timothycrosley.github.io/isort/
.. _`black`: https://black.readthedocs.io/
.. _`flake8`: https://flake8.pycqa.org/
.. _`mypy`: https://mypy.readthedocs.io/
.. _`projects`: https://packaging.python.org/glossary/#term-Project
.. _`open issues`: https://github.com/pypa/twine/issues
.. _`PyPI`: https://pypi.org/project/twine/
