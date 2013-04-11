Fuzzy attributes
================

.. module:: factory.fuzzy

Some tests may be interested in testing with fuzzy, random values.

This is handled by the :mod:`factory.fuzzy` module, which provides a few
random declarations.


FuzzyAttribute
--------------


.. class:: FuzzyAttribute

    The :class:`FuzzyAttribute` uses an arbitrary callable as fuzzer.
    It is expected that successive calls of that function return various
    values.

    .. attribute:: fuzzer

        The callable that generates random values


FuzzyChoice
-----------


.. class:: FuzzyChoice(choices)

    The :class:`FuzzyChoice` fuzzer yields random choices from the given
    iterable.

    .. note:: The passed in :attr:`choices` will be converted into a list at
              declaration time.

    .. attribute:: choices

        The list of choices to select randomly


FuzzyInteger
------------

.. class:: FuzzyInteger(low[, high])

    The :class:`FuzzyInteger` fuzzer generates random integers within a given
    inclusive range.

    The :attr:`low` bound may be omitted, in which case it defaults to 0:

    .. code-block:: pycon

        >>> FuzzyInteger(0, 42)
        >>> fi.low, fi.high
        0, 42

        >>> fi = FuzzyInteger(42)
        >>> fi.low, fi.high
        0, 42

    .. attribute:: low

        int, the inclusive lower bound of generated integers

    .. attribute:: high

        int, the inclusive higher bound of generated integers


Custom fuzzy fields
-------------------

Alternate fuzzy fields may be defined.
They should inherit from the :class:`BaseFuzzyAttribute` class, and override its
:meth:`~BaseFuzzyAttribute.fuzz` method.


.. class:: BaseFuzzyAttribute

    Base class for all fuzzy attributes.

    .. method:: fuzz(self)

        The method responsible for generating random values.
        *Must* be overridden in subclasses.
