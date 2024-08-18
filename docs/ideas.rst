Ideas
=====


This is a list of future features that may be incorporated into factory_boy:

* When a :class:`~factory.Factory` is built or created, pass the calling context throughout the calling chain instead of custom solutions everywhere
* Define a proper set of rules for the support of third-party ORMs
* Properly evaluate nested declarations (e.g ``factory.fuzzy.FuzzyDate(start_date=factory.SelfAttribute('since'))``)
