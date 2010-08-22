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

class ObjectParamsWrapper(object):
    '''A generic container that allows for getting but not setting of attributes.
    
    Attributes are set at initialization time.'''
    
    initialized = False
    
    def __init__(self, dict):
        self.dict = dict
        self.initialized = True
        
    def __setattr__(self, name, value):
        if not self.initialized:
            return super(ObjectParamsWrapper, self).__setattr__(name, value)
        else:
            raise AttributeError('Setting of object attributes is not allowed')
    
    def __getattr__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            raise AttributeError("The param '{0}' does not exist. Perhaps your declarations are out of order?".format(name))
        
class StubObject(object):
    '''A generic container.'''
    
    pass