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


FuzzyText
---------


.. class:: FuzzyText(length=12, chars=string.ascii_letters, prefix='')

    The :class:`FuzzyText` fuzzer yields random strings beginning with
    the given :attr:`prefix`, followed by :attr:`length` charactes chosen
    from the :attr:`chars` character set,
    and ending with the given :attr:`suffix`.

    .. attribute:: length

        int, the length of the random part

    .. attribute:: prefix

        text, an optional prefix to prepend to the random part

    .. attribute:: suffix

        text, an optional suffix to append to the random part

    .. attribute:: chars

        char iterable, the chars to choose from; defaults to the list of ascii
            letters and numbers.


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

.. class:: FuzzyInteger(low[, high[, step]])

    The :class:`FuzzyInteger` fuzzer generates random integers within a given
    inclusive range.

    The :attr:`low` bound may be omitted, in which case it defaults to 0:

    .. code-block:: pycon

        >>> fi = FuzzyInteger(0, 42)
        >>> fi.low, fi.high
        0, 42

        >>> fi = FuzzyInteger(42)
        >>> fi.low, fi.high
        0, 42

    .. attribute:: low

        int, the inclusive lower bound of generated integers

    .. attribute:: high

        int, the inclusive higher bound of generated integers

    .. attribute:: step

        int, the step between values in the range; for instance, a ``FuzzyInteger(0, 42, step=3)``
        might only yield values from ``[0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42]``.


FuzzyDecimal
------------

.. class:: FuzzyDecimal(low[, high[, precision=2]])

    The :class:`FuzzyDecimal` fuzzer generates random :class:`decimals <decimal.Decimal>` within a given
    inclusive range.

    The :attr:`low` bound may be omitted, in which case it defaults to 0:

    .. code-block:: pycon

        >>> FuzzyDecimal(0.5, 42.7)
        >>> fi.low, fi.high
        0.5, 42.7

        >>> fi = FuzzyDecimal(42.7)
        >>> fi.low, fi.high
        0.0, 42.7

        >>> fi = FuzzyDecimal(0.5, 42.7, 3)
        >>> fi.low, fi.high, fi.precision
        0.5, 42.7, 3

    .. attribute:: low

        decimal, the inclusive lower bound of generated decimals

    .. attribute:: high

        decimal, the inclusive higher bound of generated decimals

    .. attribute:: precision
        int, the number of digits to generate after the dot. The default is 2 digits.


FuzzyFloat
----------

.. class:: FuzzyFloat(low[, high])

    The :class:`FuzzyFloat` fuzzer provides random :class:`float` objects within a given inclusive range.

    .. code-block:: pycon

        >>> FuzzyFloat(0.5, 42.7)
        >>> fi.low, fi.high
        0.5, 42.7

        >>> fi = FuzzyFloat(42.7)
        >>> fi.low, fi.high
        0.0, 42.7


    .. attribute:: low

        decimal, the inclusive lower bound of generated floats

    .. attribute:: high

        decimal, the inclusive higher bound of generated floats

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


FuzzyPoint
----------

.. class:: FuzzyPoint(min_x, max_x=None, step_x=1,
                      min_y=None, max_y=None, step_y=None,
                      min_z=None, max_z=None, step_z=None,
                      use_z=False, converter=None)

    The :class:`FuzzyPoint` fuzzer generates random ``(x, y)`` points within
    a given inclusive range. Range values for ``y`` default to the range values
    for ``x``, so if you want to use the same range for both, you can just
    specify the values for ``x``. If only one value is provided, it is treated
    as :attr:`max_x`, and :attr:`min_x` defaults to 0.

    .. code-block:: pycon

        >>> fp = FuzzyPoint(0, 42)
        >>> fp.min_x, fp.max_x
        0, 42

        >>> fp = FuzzyPoint(42)
        >>> fp.min_x, fp.max_x
        0, 42

    You can also set :attr:`use_z` to True, in which case :class:`FuzzyPoint`
    will return ``(x, y, z)`` coordinates. Setting :attr:`min_z` or :attr:`max_z`
    will automatically set :attr:`use_z` to True.

    If you pass a :attr:`converter` function, the randomly-generated points
    will be passed to the converter function before being returned. This is
    useful if you want to use a spatial analysis library like `Shapely`_.

    .. attribute:: min_x

        int or None, the inclusive lower bound of the generated ``x`` value.
        Defaults to 0.

    .. attribute:: max_x

        int, the inclusive upper bound of the generated ``x`` value.

    .. attribute:: step_x

        int, the step between values in the ``x`` range. Defaults to 1.

    .. attribute:: min_y

        int or None, the inclusive lower bound of the generated ``y`` value.
        Defaults to the value of :attr:`min_x`.

    .. attribute:: max_y

        int or None, the inclusive upper bound of the generated ``y`` value.
        Defaults to the value of :attr:`max_x`.

    .. attribute:: step_y

        int or None, the step between values in the ``y`` range. Defaults to
        value of :attr:`step_x`.

    .. attribute:: min_z

        int or None, the inclusive lower bound of the generated ``z`` value.
        This causes the :class:`FuzzyPoint` to return ``(x, y, z)`` coordinates
        instead of ``(x, y)`` coordinates.

    .. attribute:: max_z

        int or None, the inclusive upper bound of the generated ``z`` value.
        This causes the :class:`FuzzyPoint` to return ``(x, y, z)`` coordinates
        instead of ``(x, y)`` coordinates.

    .. attribute:: step_z

        int or None, the step between values in the ``z`` range. Defaults to
        value of :attr:`step_x`.

    .. attribute:: use_z

        bool. If True, this causes the :class:`FuzzyPoint` to return ``(x, y, z)``
        coordinates instead of ``(x, y)`` coordinates, where the upper and lower
        bounds for ``z`` default to the upper and lower bounds for ``x``.

    .. attribute:: converter

        function or class. If provided, the coordinates will be passed to the
        converter and the result will be returned. For example, if you are
        using `Shapely`_, you can pass the `Point`_ class as a converter to get
        Point objects.

.. _Shapely: http://toblerity.org/shapely/
.. _Point: http://toblerity.org/shapely/manual.html#Point


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
