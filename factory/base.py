# Copyright (c) 2010 Mark Sandstrom
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import sys

from containers import ObjectParamsWrapper, StubObject
from declarations import OrderedDeclaration

# Strategies

BUILD_STRATEGY = 'build'
CREATE_STRATEGY = 'create'
STUB_STRATEGY = 'stub'

# Creation functions. Use Factory.set_creation_function() to set a creation function appropriate for your ORM.

DJANGO_CREATION = lambda class_to_create, **kwargs: class_to_create.objects.create(**kwargs)
        
# Special declarations

FACTORY_CLASS_DECLARATION = 'FACTORY_FOR'

# Factory class attributes

CLASS_ATTRIBUTE_ORDERED_DECLARATIONS = '_ordered_declarations'
CLASS_ATTRIBUTE_UNORDERED_DECLARATIONS = '_unordered_declarations'
CLASS_ATTRIBUTE_ASSOCIATED_CLASS = '_associated_class'

# Factory metaclasses

def get_factory_base(bases):
    parents = [b for b in bases if isinstance(b, BaseFactoryMetaClass)]
    if not parents:
        return None
    if len(parents) > 1:
        raise RuntimeError('You can only inherit from one Factory')
    return parents[0]

class BaseFactoryMetaClass(type):
    '''Factory metaclass for handling ordered declarations.'''
     
    def __call__(cls, **kwargs):
        '''Create an associated class instance using the default build strategy. Never create a Factory instance.'''
        
        if cls.default_strategy == BUILD_STRATEGY:
            return cls.build(**kwargs)
        elif cls.default_strategy == CREATE_STRATEGY:
            return cls.create(**kwargs)
        elif cls.default_strategy == STUB_STRATEGY:
            return cls.stub(**kwargs)
        else:
            raise BaseFactory.UnknownStrategy('Unknown default_strategy: {0}'.format(cls.default_strategy))
    
    def __new__(cls, class_name, bases, dict, extra_dict={}):
        '''Record attributes (unordered declarations) and ordered declarations for construction of
        an associated class instance at a later time.'''
        
        base = get_factory_base(bases)
        if not base:
            # If this isn't a subclass of Factory, don't do anything special.
            return super(BaseFactoryMetaClass, cls).__new__(cls, class_name, bases, dict)
        
        ordered_declarations = getattr(base, CLASS_ATTRIBUTE_ORDERED_DECLARATIONS, [])
        unordered_declarations = getattr(base, CLASS_ATTRIBUTE_UNORDERED_DECLARATIONS, [])

        for name in list(dict):
            if isinstance(dict[name], OrderedDeclaration):
                ordered_declarations = [(_name, declaration) for (_name, declaration) in ordered_declarations if _name != name]
                ordered_declarations.append((name, dict[name]))
                del dict[name]
            elif not name.startswith('__'):
                unordered_declarations = [(_name, value) for (_name, value) in unordered_declarations if _name != name]
                unordered_declarations.append((name, dict[name]))
                del dict[name]

        ordered_declarations.sort(key=lambda d: d[1].order)

        dict[CLASS_ATTRIBUTE_ORDERED_DECLARATIONS] = ordered_declarations
        dict[CLASS_ATTRIBUTE_UNORDERED_DECLARATIONS] = unordered_declarations
        
        for name, value in extra_dict.iteritems():
            dict[name] = value

        return super(BaseFactoryMetaClass, cls).__new__(cls, class_name, bases, dict)

class FactoryMetaClass(BaseFactoryMetaClass):
    '''Factory metaclass for handling class association and ordered declarations.'''
    
    ERROR_MESSAGE = '''Could not determine what class this factory is for.
    Use the {0} attribute to specify a class.'''
    ERROR_MESSAGE_AUTODISCOVERY = ERROR_MESSAGE + '''
    Also, autodiscovery failed using the name '{1}'
    based on the Factory name '{2}' in {3}.'''
    
    def __new__(cls, class_name, bases, dict):
        '''Determine the associated class based on the factory class name. Record the associated class
        for construction of an associated class instance at a later time.'''
        
        base = get_factory_base(bases)
        if not base:
            # If this isn't a subclass of Factory, don't do anything special.
            return super(FactoryMetaClass, cls).__new__(cls, class_name, bases, dict)
        
        inherited_associated_class = getattr(base, CLASS_ATTRIBUTE_ASSOCIATED_CLASS, None)
        own_associated_class = None
        used_auto_discovery = False
            
        if FACTORY_CLASS_DECLARATION in dict:
            own_associated_class = dict[FACTORY_CLASS_DECLARATION]
            del dict[FACTORY_CLASS_DECLARATION]
        else:
            factory_module = sys.modules[dict['__module__']]
            match = re.match(r'^(\w+)Factory$', class_name)
            if match:
                used_auto_discovery = True
                associated_class_name = match.group(1)
                try:
                    own_associated_class = getattr(factory_module, associated_class_name)
                except AttributeError:
                    pass
                    
        if own_associated_class != None and inherited_associated_class != None and own_associated_class != inherited_associated_class:
            format = 'These factories are for conflicting classes: {0} and {1}'
            raise Factory.AssociatedClassError(format.format(inherited_associated_class, own_associated_class))
        elif inherited_associated_class != None:
            own_associated_class = inherited_associated_class
            
        if not own_associated_class and used_auto_discovery:
            format_args = FACTORY_CLASS_DECLARATION, associated_class_name, class_name, factory_module
            raise Factory.AssociatedClassError(FactoryMetaClass.ERROR_MESSAGE_AUTODISCOVERY.format(*format_args))
        elif not own_associated_class:
            raise Factory.AssociatedClassError(FactoryMetaClass.ERROR_MESSAGE.format(FACTORY_CLASS_DECLARATION))
            
        extra_dict = {CLASS_ATTRIBUTE_ASSOCIATED_CLASS: own_associated_class}
        return super(FactoryMetaClass, cls).__new__(cls, class_name, bases, dict, extra_dict=extra_dict) 

# Factory base classes

class BaseFactory(object):
    '''Factory base support for sequences, attributes and stubs.'''
    
    class UnknownStrategy(RuntimeError): pass
    class UnsupportedStrategy(RuntimeError): pass
    
    def __new__(cls, *args, **kwargs):
        raise RuntimeError('You cannot instantiate BaseFactory')
    
    _next_sequence = 0
    
    @classmethod
    def _generate_next_sequence(cls):
        next_sequence = cls._next_sequence
        cls._next_sequence += 1
        return next_sequence
        
    @classmethod
    def attributes(cls, **kwargs):
        attributes = {}
        cls.sequence = cls._generate_next_sequence()

        for name, value in getattr(cls, CLASS_ATTRIBUTE_UNORDERED_DECLARATIONS):
            if name in kwargs:
                attributes[name] = kwargs[name]
                del kwargs[name]
            else:
                attributes[name] = value

        for name, ordered_declaration in getattr(cls, CLASS_ATTRIBUTE_ORDERED_DECLARATIONS):
            if name in kwargs:
                attributes[name] = kwargs[name]
                del kwargs[name]
            else:
                a = ObjectParamsWrapper(attributes)
                attributes[name] = ordered_declaration.evaluate(cls, a)

        for name in kwargs:
            attributes[name] = kwargs[name]

        return attributes
        
    @classmethod
    def build(cls, **kwargs):
        raise cls.UnsupportedStrategy()
    
    @classmethod
    def create(cls, **kwargs):
        raise cls.UnsupportedStrategy()
    
    @classmethod
    def stub(cls, **kwargs):
        stub_object = StubObject()
        for name, value in cls.attributes(**kwargs).iteritems():
            setattr(stub_object, name, value)
        return stub_object

class StubFactory(BaseFactory):
    __metaclass__ = BaseFactoryMetaClass

    default_strategy = STUB_STRATEGY

class Factory(BaseFactory):
    '''Factory base with build and create support.
    
    This class has the ability to support multiple ORMs by using custom creation functions.'''
    
    __metaclass__ = FactoryMetaClass
    
    default_strategy = CREATE_STRATEGY
    
    class AssociatedClassError(RuntimeError): pass
    
    _creation_function = (DJANGO_CREATION,)  # Using a tuple to keep the creation function from turning into an instance method
    @classmethod
    def set_creation_function(cls, creation_function):
        cls._creation_function = (creation_function,)
    @classmethod
    def get_creation_function(cls):
        return cls._creation_function[0]
    
    @classmethod
    def build(cls, **kwargs):
        return getattr(cls, CLASS_ATTRIBUTE_ASSOCIATED_CLASS)(**cls.attributes(**kwargs))
        
    @classmethod
    def create(cls, **kwargs):
        return cls.get_creation_function()(getattr(cls, CLASS_ATTRIBUTE_ASSOCIATED_CLASS), **cls.attributes(**kwargs))
