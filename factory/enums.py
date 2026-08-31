# Copyright: See the LICENSE file.

# Strategies
BUILD_STRATEGY = 'build'
CREATE_STRATEGY = 'create'
STUB_STRATEGY = 'stub'


#: String for splitting an attribute name into a
#: (subfactory_name, subfactory_field) tuple.
SPLITTER = '__'


# Target build phase, for declarations
class BuilderPhase:
    #: During attribute resolution/computation
    ATTRIBUTE_RESOLUTION = 'attributes'

    #: Once the target object has been built
    POST_INSTANTIATION = 'post_instance'


def get_builder_phase(obj):
    return getattr(obj, 'FACTORY_BUILDER_PHASE', None)


def _contains_declaration(value):
    if get_builder_phase(value):
        return True
    if isinstance(value, (list, tuple)):
        return any(_contains_declaration(v) for v in value)
    if isinstance(value, dict):
        return any(_contains_declaration(v) for v in value.values())
    return False
