# Copyright: See the LICENSE file.

from .base import (
    BaseDictFactory,
    BaseListFactory,
    DictFactory,
    Factory,
    ListFactory,
    StubFactory,
    use_strategy,
)
from .declarations import (
    ContainerAttribute,
    Dict,
    Iterator,
    LazyAttribute,
    LazyAttributeSequence,
    LazyFunction,
    List,
    Maybe,
    PostGeneration,
    PostGenerationMethodCall,
    RelatedFactory,
    RelatedFactoryList,
    SelfAttribute,
    Sequence,
    SubFactory,
    Trait,
)
from .enums import BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY
from .errors import FactoryError
from .faker import Faker
from .helpers import (
    build,
    build_batch,
    container_attribute,
    create,
    create_batch,
    debug,
    generate,
    generate_batch,
    iterator,
    lazy_attribute,
    lazy_attribute_sequence,
    make_factory,
    post_generation,
    sequence,
    simple_generate,
    simple_generate_batch,
    stub,
    stub_batch,
)

try:
    from . import alchemy
except ImportError:
    pass
try:
    from . import django
except ImportError:
    pass
try:
    from . import mogo
except ImportError:
    pass
try:
    from . import mongoengine
except ImportError:
    pass

__author__ = 'Raphaël Barrois <raphael.barrois+fboy@polytechnique.org>'
try:
    # Python 3.8+
    from importlib.metadata import version

    __version__ = version("factory_boy")
except ImportError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("factory_boy").version
