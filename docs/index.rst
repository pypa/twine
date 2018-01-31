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

Building the documentation
--------------------------

Additions and edits to twine's documentation are welcome and appreciated. To
build the docs locally, first set up a virtual environment and activate it,
using Python 3.6 as the Python version in the virtual environment. Then install
the following:

Install twine:

.. code-block:: console

  pip install twine

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
.. _`plugin`: https://github.com/bitprophet/releases
