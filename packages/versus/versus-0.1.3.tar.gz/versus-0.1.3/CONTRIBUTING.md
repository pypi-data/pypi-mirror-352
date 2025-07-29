Contributor guidelines
======================

.. _documentation: https://versus.readthedocs.io/#writing-documentation
.. _testing: https://versus.readthedocs.io/#testing
.. _pre-commit: https://pre-commit.com/#installation
.. _black: https://black.readthedocs.io/
.. _isort: https://pycqa.github.io/isort/
.. _doc8: https://doc8.readthedocs.io/
.. _ruff: https://beta.ruff.rs/docs/
.. _pip-tools: https://pip-tools.readthedocs.io/
.. _uv: https://docs.astral.sh/uv/
.. _tox: https://tox.wiki
.. _issues: https://github.com/barseghyanartur/versus/issues
.. _discussions: https://github.com/barseghyanartur/versus/discussions
.. _pull request: https://github.com/barseghyanartur/versus/pulls
.. _support: https://versus.readthedocs.io/#support
.. _installation: https://versus.readthedocs.io/#installation
.. _prerequisites: https://versus.readthedocs.io/#prerequisites
.. _versions manifest: https://github.com/actions/python-versions/blob/main/versions-manifest.json

Developer prerequisites
-----------------------
pre-commit
~~~~~~~~~~
Refer to `pre-commit`_ for installation instructions.

TL;DR:

.. code-block:: sh

    curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
    uv tool install pre-commit  # Install pre-commit
    pre-commit install  # Install pre-commit hooks

Installing `pre-commit`_ will ensure you adhere to the project code quality
standards.

Code standards
--------------
`ruff`_ and `doc8`_ will be automatically triggered by `pre-commit`_.

`ruff`_ is configured to do the job of `black`_ and `isort`_ as well.

Still, if you want to run checks manually:

.. code-block:: sh

    make doc8
    make ruff

Requirements
------------
Requirements are compiled using `uv`_.

.. code-block:: sh

    make compile-requirements

Virtual environment
-------------------
You are advised to work in virtual environment.

TL;DR:

.. code-block:: sh

    python -m venv env
    pip install -e .[all]

Documentation
-------------
Check the `documentation`_.

Testing
-------
Check `testing`_.

If you introduce changes or fixes, make sure to test them locally using
all supported environments. For that use `tox`_.

.. code-block:: sh

    tox

In any case, GitHub Actions will catch potential errors, but using tox speeds
things up.

For a quick test of the package and all examples, use the following `Makefile`
command:

.. code-block:: sh

    make test-all

Releasing
---------
**Sequence of steps:**

#. Clean and build

    .. code-block:: sh

        make clean
        make build

#. Check the build

    .. code-block:: sh

        make check-build

#. Test release on test.pypi.org. Make sure to check it before moving forward.

    .. code-block:: sh

        make test-release

#. Release

    .. code-block:: sh

        make release

Pull requests
-------------
You can contribute to the project by making a `pull request`_.

For example:

- To fix documentation typos.
- To improve documentation (for instance, to add new recipe or fix
  an existing recipe that doesn't seem to work).
- To introduce a new feature (for instance, add support for a non-supported
  file type).

**Good to know:**

- This library consists of a single ``versus.py`` module. That module is
  dependency free, self-contained (includes all tests) and portable.
  Do not submit pull requests splitting the ``versus.py`` module into small
  parts. Pull requests with external dependencies in ``versus.py`` module will
  not be accepted either.

**General list to go through:**

- Does your change require documentation update?
- Does your change require update to tests?
- Does your change rely on third-party package or a cloud based service?
  If so, please consider turning it into a dedicated standalone package,
  since this library is dependency free (and will always stay so).

**When fixing bugs (in addition to the general list):**

- Make sure to add regression tests.

**When adding a new feature (in addition to the general list):**

- Make sure to update the documentation.

GitHub Actions
--------------
Only non-EOL versions of Python and other software ``versus`` aims to
integrate with are supported.

On GitHub Actions includes tests with all non-EOL Python versions.
Future, non-stable versions of Python are being tested too, so that new
features/incompatibilities could be seen and adopted early.

For the list of Python versions supported by GitHub, see GitHub Actions
`versions manifest`_.

Questions
---------
Questions can be asked on GitHub `discussions`_.

Issues
------
For reporting a bug or filing a feature request, use GitHub `issues`_.

**Do not report security issues on GitHub**. Check the `support`_ section.
