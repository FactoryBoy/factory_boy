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

class OrderedDeclaration(object):
    '''A factory declaration.
    
    Ordered declarations keep track of the order in which they're defined so that later declarations
    can refer to attributes created by earlier declarations when the declarations are evaluated.'''
    _next_order = 0
    
    def __init__(self):
        self.order = self.next_order()
        
    @classmethod
    def next_order(cls):
        next_order = cls._next_order
        cls._next_order += 1
        return next_order
        
    def evaluate(self, factory, attributes):
        '''Evaluate this declaration.
        
        Args:
            factory: The factory this declaration was defined in.
            attributes: The attributes created by the unordered and ordered declarations up to this point.'''
        
        raise NotImplementedError('This is an abstract method')

class LazyAttribute(OrderedDeclaration):
    def __init__(self, function):
        super(LazyAttribute, self).__init__()
        self.function = function
    
    def evaluate(self, factory, attributes):
        return self.function(attributes)

class Sequence(OrderedDeclaration):
    def __init__(self, function, type=str):
        super(Sequence, self).__init__()
        self.function = function
        self.type = type
    
    def evaluate(self, factory, attributes):
        return self.function(self.type(factory.sequence))

class LazyAttributeSequence(Sequence):
    def evaluate(self, factory, attributes):
        return self.function(attributes, self.type(factory.sequence))

# Decorators... in case lambdas don't cut it

def lazy_attribute(func):
    return LazyAttribute(func)

def sequence(func):
    return Sequence(func)

def lazy_attribute_sequence(func):
    return LazyAttributeSequence(func)