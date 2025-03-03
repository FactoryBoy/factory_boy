# Copyright: See the LICENSE file.


class FactoryError(Exception):
    """Any exception raised by factory_boy."""


class AssociatedClassError(FactoryError):
    """Exception for Factory subclasses lacking Meta.model."""


class UnknownStrategy(FactoryError):
    """Raised when a factory uses an unknown strategy."""


class UnsupportedStrategy(FactoryError):
    """Raised when trying to use a strategy on an incompatible Factory."""


class CyclicDefinitionError(FactoryError):
    """Raised when a cyclical declaration occurs."""


class InvalidDeclarationError(FactoryError):
    """Raised when a sub-declaration has no related declaration.

    This means that the user declared 'foo__bar' without adding a declaration
    at 'foo'.
    """


class LazyAttributeError(AttributeError):
    """ A lazily evaluated version of AttributeError.

    To be used when generating the error message is expensive.
    """
    def __init__(self, message, *args):
        super().__init__()
        self._message = message
        self._args = args

    def __str__(self):
        return self._message % self._args
