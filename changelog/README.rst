Changelog Entries
=================

The ``docs/changelog.rst`` file is managed using `towncrier`_, and all
non-trivial changes must be accompanied by a changelog entry.

Adding a changelog entry
------------------------

First open a pull request with the change you want to make, ideally referencing
an open issue. Then, create a file in the ``changelog/`` directory named
``{number}.{type}.rst``, where ``{number}`` is the PR number, and ``{type}`` is
``feature``, ``bugfix``, ``doc``, ``removal``, or ``misc``.

For example, if your PR number is ``1234`` and it's fixing a bug, then you
would create ``changelog/1234.bugfix.rst``. PRs can span multiple categories by
creating multiple files: if you added a feature and deprecated/removed the old
feature in one PR, you would create ``changelog/1234.feature.rst`` and
``changelog/1234.removal.rst``.

Contents of a changelog entry
-----------------------------

A changelog entry is meant for end users and should only contain details
relevant to them. In order to maintain a consistent style, please keep the
entry to the point, in sentence case, shorter than 80 characters, and in an
imperative tone. An entry should complete the sentence "This change will ...".
If one line is not enough, use a summary line in an imperative tone, followed
by a description of the change in one or more paragraphs, each wrapped at 80
characters and separated by blank lines.

You don't need to reference the pull request or issue number in a changelog
entry, since ``towncrier`` will add a link using the number in the file name,
and the pull request should reference an issue number. Similarly, you don't
need to add your name to the entry, since that will be associated with the pull
request.

Changelog entries are rendered using `reStructuredText`_, but they should only
have minimal formatting (such as ````monospaced text````).

.. _`towncrier`: https://pypi.org/project/towncrier/
.. _`reStructuredText`: https://www.writethedocs.org/guide/writing/reStructuredText/
