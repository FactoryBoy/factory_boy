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


FuzzyDate
---------

.. class:: FuzzyDate(start_date[, end_date])

    The :class:`FuzzyDate` fuzzer generates random dates within a given
    inclusive range.

    The :attr:`end_date` bound may be omitted, in which case it defaults to the current date:

    .. code-block:: pycon

        >>> fd = FuzzyDate(datetime.date(2008, 1, 1))
        >>> fd.start_date, fd.end_date
        datetime.date(2008, 1, 1), datetime.date(2013, 4, 16)

    .. attribute:: start_date

        :class:`datetime.date`, the inclusive lower bound of generated dates

    .. attribute:: end_date

        :class:`datetime.date`, the inclusive higher bound of generated dates


FuzzyDateTime
-------------

.. class:: FuzzyDateTime(start_dt[, end_dt], tz=UTC, force_year=None, force_month=None, force_day=None, force_hour=None, force_minute=None, force_second=None, force_microsecond=None)

    The :class:`FuzzyDateTime` fuzzer generates random timezone-aware datetime within a given
    inclusive range.

    The :attr:`end_dt` bound may be omitted, in which case it defaults to ``datetime.datetime.now()``
    localized into the UTC timezone.

    .. code-block:: pycon

        >>> fdt = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC))
        >>> fdt.start_dt, fdt.end_dt
        datetime.datetime(2008, 1, 1, tzinfo=UTC), datetime.datetime(2013, 4, 21, 19, 13, 32, 458487, tzinfo=UTC)


    The ``force_XXX`` keyword arguments force the related value of generated datetimes:

    .. code-block:: pycon

        >>> fdt = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), datetime.datetime(2009, 1, 1, tzinfo=UTC),
        ...     force_day=3, force_second=42)
        >>> fdt.evaluate(2, None, False)  # Actual code used by ``SomeFactory.build()``
        datetime.datetime(2008, 5, 3, 12, 13, 42, 124848, tzinfo=UTC)


    .. attribute:: start_dt

        :class:`datetime.datetime`, the inclusive lower bound of generated datetimes

    .. attribute:: end_dt

        :class:`datetime.datetime`, the inclusive upper bound of generated datetimes


    .. attribute:: force_year

        int or None; if set, forces the :attr:`~datetime.datetime.year` of generated datetime.

    .. attribute:: force_month

        int or None; if set, forces the :attr:`~datetime.datetime.month` of generated datetime.

    .. attribute:: force_day

        int or None; if set, forces the :attr:`~datetime.datetime.day` of generated datetime.

    .. attribute:: force_hour

        int or None; if set, forces the :attr:`~datetime.datetime.hour` of generated datetime.

    .. attribute:: force_minute

        int or None; if set, forces the :attr:`~datetime.datetime.minute` of generated datetime.

    .. attribute:: force_second

        int or None; if set, forces the :attr:`~datetime.datetime.second` of generated datetime.

    .. attribute:: force_microsecond

        int or None; if set, forces the :attr:`~datetime.datetime.microsecond` of generated datetime.


FuzzyNaiveDateTime
------------------

.. class:: FuzzyNaiveDateTime(start_dt[, end_dt], force_year=None, force_month=None, force_day=None, force_hour=None, force_minute=None, force_second=None, force_microsecond=None)

    The :class:`FuzzyNaiveDateTime` fuzzer generates random naive datetime within a given
    inclusive range.

    The :attr:`end_dt` bound may be omitted, in which case it defaults to ``datetime.datetime.now()``:

    .. code-block:: pycon

        >>> fdt = FuzzyNaiveDateTime(datetime.datetime(2008, 1, 1))
        >>> fdt.start_dt, fdt.end_dt
        datetime.datetime(2008, 1, 1), datetime.datetime(2013, 4, 21, 19, 13, 32, 458487)


    The ``force_XXX`` keyword arguments force the related value of generated datetimes:

    .. code-block:: pycon

        >>> fdt = FuzzyNaiveDateTime(datetime.datetime(2008, 1, 1), datetime.datetime(2009, 1, 1),
        ...     force_day=3, force_second=42)
        >>> fdt.evaluate(2, None, False)  # Actual code used by ``SomeFactory.build()``
        datetime.datetime(2008, 5, 3, 12, 13, 42, 124848)


    .. attribute:: start_dt

        :class:`datetime.datetime`, the inclusive lower bound of generated datetimes

    .. attribute:: end_dt

        :class:`datetime.datetime`, the inclusive upper bound of generated datetimes


    .. attribute:: force_year

        int or None; if set, forces the :attr:`~datetime.datetime.year` of generated datetime.

    .. attribute:: force_month

        int or None; if set, forces the :attr:`~datetime.datetime.month` of generated datetime.

    .. attribute:: force_day

        int or None; if set, forces the :attr:`~datetime.datetime.day` of generated datetime.

    .. attribute:: force_hour

        int or None; if set, forces the :attr:`~datetime.datetime.hour` of generated datetime.

    .. attribute:: force_minute

        int or None; if set, forces the :attr:`~datetime.datetime.minute` of generated datetime.

    .. attribute:: force_second

        int or None; if set, forces the :attr:`~datetime.datetime.second` of generated datetime.

    .. attribute:: force_microsecond

        int or None; if set, forces the :attr:`~datetime.datetime.microsecond` of generated datetime.


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
