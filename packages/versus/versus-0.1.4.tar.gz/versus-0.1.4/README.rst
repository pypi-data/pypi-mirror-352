======
versus
======
.. External references

.. _Django: https://www.djangoproject.com/
.. _Pydantic: https://docs.pydantic.dev/
.. _sphinx-autobuild: https://github.com/sphinx-doc/sphinx-autobuild

.. Internal references

.. _versus: https://github.com/barseghyanartur/versus/
.. _Read the Docs: http://versus.readthedocs.io/
.. _Contributor guidelines: https://versus.readthedocs.io/en/latest/contributor_guidelines.html
.. _llms.txt: https://versus.readthedocs.io/en/latest/llms.txt
.. _Tweak your test/coverage configuration: https://versus.readthedocs.io/en/latest/test_configuration_tweaks.html

Package version comparison made easy.

.. image:: https://img.shields.io/pypi/v/versus.svg
   :target: https://pypi.python.org/pypi/versus
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/versus.svg
    :target: https://pypi.python.org/pypi/versus/
    :alt: Supported Python versions

.. image:: https://github.com/barseghyanartur/versus/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/barseghyanartur/versus/actions
   :alt: Build Status

.. image:: https://readthedocs.org/projects/versus/badge/?version=latest
    :target: http://versus.readthedocs.io
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/docs-llms.txt-blue
    :target: https://versus.readthedocs.io/en/latest/llms.txt
    :alt: llms.txt - documentation for LLMs

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/barseghyanartur/versus/#License
   :alt: MIT

.. image:: https://coveralls.io/repos/github/barseghyanartur/versus/badge.svg?branch=main&service=github
    :target: https://coveralls.io/github/barseghyanartur/versus?branch=main
    :alt: Coverage

`versus`_ is a standalone, portable, dependency-free Python module for
retrieving and comparing installed package versions. It supports variety of
lookups, such as ``lte``, ``lt``, ``gte``, ``gt`` and ``eq``.

Prerequisites
=============
Python 3.9+

Installation
============
pip
---

.. code-block:: sh

    pip install versus

Download and copy
-----------------
``versus.py`` is the sole, self-contained module of the package. It includes
tests too. If it's more convenient to you, you could simply download the
``versus.py`` module and include it in your repository.

Since tests are included, it won't have a negative impact on your test
coverage (you might need to `tweak your test/coverage configuration`_).

Documentation
=============
- Documentation is available on `Read the Docs`_.
- For guidelines on contributing check the `Contributor guidelines`_.

Usage
=====
Comparing `Django`_ versions.

.. code-block:: python
    :name: test_get_version

    from versus import get_version

    django_version = get_version("django")
    print(django_version)  # 5.2.1

    django_version.gte("4.2")  # True
    django_version.gte("5.2")  # True
    django_version.gte("5.2.1")  # True
    django_version.gte("5.2.2")  # False

Comparing `sphinx-autobuild`_ versions:

.. continue: test_get_version
.. code-block:: python
    :name: test_get_version_sphinx_autobuild

    sphinx_autobuild_version = get_version("sphinx-autobuild")
    print(sphinx_autobuild_version)  # 2024.10.3

    sphinx_autobuild_version.gte("1.0")  # True
    sphinx_autobuild_version.gte("2024.09")  # True
    sphinx_autobuild_version.gte("2024.11")  # False
    sphinx_autobuild_version.lte("2024.11")  # True

Non-existent/non-installed package lookup would return ``None``:

.. continue: test_get_version
.. code-block:: python
    :name: test_get_version_nonexistent_package

    nonexistent_package = get_version("nonexistent-package")
    print(nonexistent_package)  # None

Tests
=====

Run the tests with unittest:

.. code-block:: sh

    python -m unittest versus

Or pytest:

.. code-block:: sh

    pytest

Writing documentation
=====================

Keep the following hierarchy.

.. code-block:: text

    =====
    title
    =====

    header
    ======

    sub-header
    ----------

    sub-sub-header
    ~~~~~~~~~~~~~~

    sub-sub-sub-header
    ^^^^^^^^^^^^^^^^^^

    sub-sub-sub-sub-header
    ++++++++++++++++++++++

    sub-sub-sub-sub-sub-header
    **************************

License
=======

MIT

Support
=======
For security issues contact me at the e-mail given in the `Author`_ section.

For overall issues, go to `GitHub <https://github.com/barseghyanartur/versus/issues>`_.

Author
======

Artur Barseghyan <artur.barseghyan@gmail.com>
