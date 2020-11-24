3.2.1.dev23+gafbf79f (2020-11-24)
---------------------------------

Features
^^^^^^^^

- Print files to be uploaded using ``upload --verbose`` (`#670 <https://github.com/pypa/twine/issues/670>`_)
- Print configuration file location when using ``upload --verbose`` (`#675 <https://github.com/pypa/twine/issues/675>`_)
- Print source and values of credentials when using ``upload --verbose`` (`#685 <https://github.com/pypa/twine/issues/685>`_)
- Add support for Python 3.9 (`#708 <https://github.com/pypa/twine/issues/708>`_)
- Turn warnings into errors when using ``check --strict`` (`#715 <https://github.com/pypa/twine/issues/715>`_)


Bugfixes
^^^^^^^^

- Make password optional when using ``upload --client-cert`` (`#678 <https://github.com/pypa/twine/issues/678>`_)
- Support more Nexus versions with ``upload --skip-existing`` (`#693 <https://github.com/pypa/twine/issues/693>`_)
- Support Gitlab Enterprise with ``upload --skip-existing`` (`#698 <https://github.com/pypa/twine/issues/698>`_)
- Show a better error message for malformed files (`#714 <https://github.com/pypa/twine/issues/714>`_)


Improved Documentation
^^^^^^^^^^^^^^^^^^^^^^

- Adopt PSF code of conduct (`#680 <https://github.com/pypa/twine/issues/680>`_)
