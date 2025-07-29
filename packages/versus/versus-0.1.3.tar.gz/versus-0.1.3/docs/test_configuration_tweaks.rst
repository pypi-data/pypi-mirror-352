Test/coverage configuration tweaks
==================================

If you decide to include ``versus`` into your code/package, the
easiest way to get the ``versus`` tests running is to create a
sibling module named ``test_versus.py`` in the same directory where
the ``versus.py`` is, with the following content:

*Filename: test_versus.py*

.. code-block:: python
    :name: test_versus

    from versus import *  # noqa
