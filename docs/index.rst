.. twine documentation master file, created by
   sphinx-quickstart on Tue Aug 13 11:51:54 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to twine's documentation!
=================================

Twine is `a utility`_ for interacting with PyPI.

Currently it only supports registering `projects`_ and uploading
`distributions`_.

The goal is to improve PyPI interaction by improving security and
testability. Ideally, ``pip`` and ``twine`` will merge into a single
tool.

Please see `the GitHub repository`_ for code and more documentation,
and the `Python Packaging User Guide`_ for user documentation. You can
also join ``#pypa`` or ``#pypa-dev`` `on Freenode`_, or the `pypa-dev
mailing list`_, to ask questions or get involved.


Contents:

.. toctree::
   :maxdepth: 2

   changelog

Getting Started
---------------

We are happy you have decided to contribute to twine.

To set up your development environment, first fork the twine repository on
GitHub, using the ``fork`` button on the upper right-hand corner of the page
for the `main twine repository`_.

Then, go to your fork of twine on GitHub. The URL will be in the following
format:

.. code-block:: console

  https://github.com/<username>/twine

Your GitHub username will appear where ``<username>`` is in the example URL
above.

Now, use ``git clone`` to download the code from your fork of the repository:

.. code-block:: console

  git clone https://github.com/<username>/twine

As in the URL above, ``<username>`` is your GitHub username.

Add the main twine repository as ``upstream``:

.. code-block:: console

  git remote add upstream https://github.com/pypa/twine

This allows you to easily keep your local copy and your GitHub fork of the code
current with any changes in the main twine repository.

To make sure you have set up everything correctly, the output of this command:

.. code-block:: console

  git remote -v

Should be the following:

.. code-block:: console

  origin  https://github.com/<username>/twine.git (fetch)
  origin  https://github.com/<username>/twine.git (push)
  upstream  https://github.com/pypa/twine.git (fetch)
  upstream  https://github.com/pypa/twine.git (push)

Your username on GitHub should replace ``<username>`` in the example above.

It is important to keep your development environment isolated, so that twine
and its dependencies do not interfere with packages already installed on your
machine.  We will use a virtual environment for the development environment for
twine. You can use `virtualenv`_ or `pipenv`_ to isolate your development
environment.

Activate your virtual environment. Then, run the following command:

.. code-block:: console

  pip install -e /path/to/your/local/twine

Now, in your virtual environment, ``twine`` is pointing at your local copy, so
when you have made changes, you can easily see their effect.

Testing
-------

Tests with twine are run using `tox`_, and tested against the following Python
versions: 2.7, 3.4, 3,5, and 3.6. To run these tests locally, you will need to
have these versions of Python installed on your machine.

If you are using pipenv to manage your virtual environment, you may need the
`tox-pipenv`_ plugin so that tox can use pipenv environments instead of
virtualenvs.

Building the documentation
--------------------------

Additions and edits to twine's documentation are welcome and appreciated. To
build the docs locally, first set up a virtual environment and activate it,
using Python 3.6 as the Python version in the virtual environment. Then install
the following:

Install Sphinx:

.. code-block:: console

  pip install Sphinx

Install the ``releases`` `plugin`_ and the Read the Docs theme for Sphinx:

.. code-block:: console

  pip install -e git+https://github.com/bitprophet/releases/#egg=releases
  pip install sphinx_rtd_theme

Change directories to the ``docs`` directory, and then run:

.. code-block:: console

  sphinx-build -b html . _build

The docs will be visible at ``twine/docs/_build/index.html``.

When you have made your changes to the docs, please lint them before making a
pull request.

Install the linter:

.. code-block:: console

  pip install doc8

Then, run the linter in the ``twine/docs`` directory:

.. code-block:: console

    doc8 .


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
