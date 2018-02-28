.. twine documentation master file, created by
   sphinx-quickstart on Tue Aug 13 11:51:54 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to twine's documentation!
=================================

Twine is `a utility`_ for interacting with PyPI.

Currently it only supports registering `projects`_ and uploading
`distributions`_.

The goal of ``twine`` is to improve PyPI interaction by improving
security and testability. In the future, ``pip`` and ``twine`` may
merge into a single tool; see `discussion
<https://github.com/pypa/packaging-problems/issues/60>`_ for ongoing
discussion.

Please see `the GitHub repository`_ for code and more documentation,
and the `Python Packaging User Guide`_ for user documentation. You can
also join ``#pypa`` or ``#pypa-dev`` `on Freenode`_, or the `pypa-dev
mailing list`_, to ask questions or get involved.

Overview
--------

Twine is a command-line tool for interacting with PyPI securely over HTTPS. Its
command line arguments are parsed in ``twine/cli.py``. Currently, twine
has two principal functions: uploading new packages and registering new
`projects`_. The code for registering new projects is in
``twine/commands/register.py``, and the code for uploading is in
``twine/commands/upload.py``. The file ``twine/package.py``
contains a single class, ``PackageFile``, which hashes the project files and
extracts their metadata. The file ``twine/repository.py`` contains the
``Repository`` class, whose methods control the URL the package is uploaded to
(which the user can specify either as a default, in the ``.pypirc`` file, or
pass on the command line), and the methods that upload the package securely to
a URL.

Contents:

.. toctree::
   :maxdepth: 2

   changelog

Getting Started
---------------

We are happy you have decided to contribute to twine.

It is important to keep your development environment isolated, so that twine
and its dependencies do not interfere with packages already installed on your
machine.  We will use a virtual environment for the development environment for
twine. You can use `virtualenv`_ or `pipenv`_ to isolate your development
environment.

Clone the twine repository from GitHub, and then activate your virtual
environment. Then, run the following command:

.. code-block:: console

  pip install -e /path/to/your/local/twine

Now, in your virtual environment, ``twine`` is pointing at your local copy, so
when you have made changes, you can easily see their effect.

Testing
-------

Tests with twine are run using `tox`_, and tested against the following Python
versions: 2.7, 3.4, 3,5, and 3.6. To run these tests locally, you will need to
have these versions of Python installed on your machine.

If you are using ``pipenv`` to manage your virtual environment, you
may need the `tox-pipenv`_ plugin so that tox can use pipenv
environments instead of virtualenvs.

Building the documentation
--------------------------

Additions and edits to twine's documentation are welcome and appreciated. To
build the docs locally, first set up a virtual environment and activate it,
using Python 3.6 as the Python version in the virtual environment. Example:

.. code-block:: console

  mkvirtualenv -p /usr/bin/python3.6 twine

Then install ``tox`` and build the docs using ``tox``:

.. code-block:: console

  pip install tox
  tox -e docs

The HTML of the docs will be visible in this directory: ``twine/docs/_build/``.

When you have made your changes to the docs, please lint them before making a
pull request. To run the linter from the root directory:

.. code-block:: console

    doc8 docs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`a utility`: https://pypi.python.org/pypi/twine
.. _`projects`: https://packaging.python.org/glossary/#term-project
.. _`distributions`: https://packaging.python.org/glossary/#term-distribution-package
.. _`Warehouse`: https://github.com/pypa/warehouse
.. _`the GitHub repository`: https://github.com/pypa/twine
.. _`Python Packaging User Guide`: https://packaging.python.org/tutorials/distributing-packages/
.. _`on Freenode`: https://webchat.freenode.net/?channels=%23pypa-dev,pypa
.. _`pypa-dev mailing list`: https://groups.google.com/forum/#!forum/pypa-dev
.. _`main twine repository`: https://github.com/pypa/twine
.. _`virtualenv`: https://virtualenv.pypa.io/en/stable/installation/
.. _`pipenv`: https://pipenv.readthedocs.io/en/latest/
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`tox-pipenv`: https://pypi.python.org/pypi/tox-pipenv
.. _`plugin`: https://github.com/bitprophet/releases
