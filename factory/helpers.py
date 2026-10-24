# Copyright: See the LICENSE file.


"""Simple wrappers around Factory class definition."""

import contextlib
import logging
import typing as T

from . import base, declarations

ModelT = T.TypeVar('ModelT')


@contextlib.contextmanager
def debug(logger: str = 'factory', stream: T.Optional[T.TextIO] = None) -> T.Iterator[None]:
    logger_obj = logging.getLogger(logger)
    old_level = logger_obj.level

    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    logger_obj.addHandler(handler)
    logger_obj.setLevel(logging.DEBUG)

    try:
        yield
    finally:
        logger_obj.setLevel(old_level)
        logger_obj.removeHandler(handler)


def make_factory(klass: T.Type[ModelT], **kwargs: T.Any) -> T.Type[base.Factory[ModelT]]:
    """Create a new, simple factory for the given class."""
    factory_name = '%sFactory' % klass.__name__

    class Meta:
        model = klass

    kwargs['Meta'] = Meta
    base_class = kwargs.pop('FACTORY_CLASS', base.Factory)

    factory_class = type(base.Factory).__new__(type(base.Factory), factory_name, (base_class,), kwargs)
    factory_class.__name__ = '%sFactory' % klass.__name__
    factory_class.__doc__ = 'Auto-generated factory for class %s' % klass
    return factory_class


def build(klass: T.Type[ModelT], **kwargs: T.Any) -> ModelT:
    """Create a factory for the given class, and build an instance."""
    return make_factory(klass, **kwargs).build()


def build_batch(klass: T.Type[ModelT], size: int, **kwargs: T.Any) -> T.List[ModelT]:
    """Create a factory for the given class, and build a batch of instances."""
    return make_factory(klass, **kwargs).build_batch(size)


def create(klass: T.Type[ModelT], **kwargs: T.Any) -> ModelT:
    """Create a factory for the given class, and create an instance."""
    return make_factory(klass, **kwargs).create()


def create_batch(klass: T.Type[ModelT], size: int, **kwargs: T.Any) -> T.List[ModelT]:
    """Create a factory for the given class, and create a batch of instances."""
    return make_factory(klass, **kwargs).create_batch(size)


def stub(klass: type, **kwargs: T.Any) -> T.Any:
    """Create a factory for the given class, and stub an instance."""
    return make_factory(klass, **kwargs).stub()


def stub_batch(klass: type, size: int, **kwargs: T.Any) -> T.List[T.Any]:
    """Create a factory for the given class, and stub a batch of instances."""
    return make_factory(klass, **kwargs).stub_batch(size)


def generate(klass: type, strategy: str, **kwargs: T.Any) -> T.Any:
    """Create a factory for the given class, and generate an instance."""
    return make_factory(klass, **kwargs).generate(strategy)


def generate_batch(klass: type, strategy: str, size: int, **kwargs: T.Any) -> T.List[T.Any]:
    """Create a factory for the given class, and generate instances."""
    return make_factory(klass, **kwargs).generate_batch(strategy, size)


def simple_generate(klass: type, create: bool, **kwargs: T.Any) -> T.Any:
    """Create a factory for the given class, and simple_generate an instance."""
    return make_factory(klass, **kwargs).simple_generate(create)


def simple_generate_batch(klass: type, create: bool, size: int, **kwargs: T.Any) -> T.List[T.Any]:
    """Create a factory for the given class, and simple_generate instances."""
    return make_factory(klass, **kwargs).simple_generate_batch(create, size)


def lazy_attribute(func: T.Callable[[T.Any], T.Any]) -> declarations.LazyAttribute:
    return declarations.LazyAttribute(func)


def iterator(func: T.Callable[[], T.Iterable[T.Any]]) -> declarations.Iterator:
    """Turn a generator function into an iterator attribute."""
    return declarations.Iterator(func())


def sequence(func: T.Callable[[T.Any], T.Any]) -> declarations.Sequence:
    # Not Callable[[int], Any]: used on an unannotated method, the function's
    # first parameter is inferred as the factory class, not as an int.
    return declarations.Sequence(func)


def lazy_attribute_sequence(func: T.Callable[[T.Any, int], T.Any]) -> declarations.LazyAttributeSequence:
    return declarations.LazyAttributeSequence(func)


def container_attribute(
    func: T.Callable[[T.Any, T.Tuple[T.Any, ...]], T.Any],
) -> declarations.ContainerAttribute:
    return declarations.ContainerAttribute(func, strict=False)


def post_generation(fun: T.Callable[..., T.Any]) -> declarations.PostGeneration:
    return declarations.PostGeneration(fun)
