Ideas
=====


This is a list of future features that may be incorporated into factory_boy:

* **A 'options' attribute**: instead of adding more class-level constants, use a django-style ``class Meta`` Factory attribute with all options there
* **factory-local fields**: Allow some fields to be available while building attributes,
  but not passed to the associated class.
  For instance, a ``global_kind`` field would be used to select values for many other fields.

