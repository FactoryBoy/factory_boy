import unittest

from factory import Factory, StubFactory, LazyAttribute, Sequence, LazyAttributeSequence, lazy_attribute, sequence, lazy_attribute_sequence
from factory import CREATE_STRATEGY, BUILD_STRATEGY, STUB_STRATEGY

class TestObject(object):
    def __init__(self, one=None, two=None, three=None, four=None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four

class FakeDjangoModel(object):
    class FakeDjangoManager(object):  
        def create(self, **kwargs):
            fake_model = FakeDjangoModel(**kwargs)
            fake_model.id = 1
            return fake_model
    
    objects = FakeDjangoManager()
    
    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
            self.id = None

class TestModel(FakeDjangoModel):
    pass

class FactoryTestCase(unittest.TestCase):
    def testAttribute(self):
        class TestObjectFactory(Factory):
            one = 'one'
            
        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')    
    
    def testSequence(self):
        class TestObjectFactory(Factory):
            one = Sequence(lambda n: 'one' + n)
            two = Sequence(lambda n: 'two' + n)
            
        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')
        
        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'one1')
        self.assertEqual(test_object1.two, 'two1')
        
    def testLazyAttribute(self):
        class TestObjectFactory(Factory):
            one = LazyAttribute(lambda a: 'abc' )
            two = LazyAttribute(lambda a: a.one + ' xyz')
            
        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'abc')
        self.assertEqual(test_object.two, 'abc xyz')
        
    def testLazyAttributeNonExistentParam(self):
        class TestObjectFactory(Factory):
            one = LazyAttribute(lambda a: a.does_not_exist )
            
        try:
            TestObjectFactory()
            self.fail()
        except AttributeError as e:
            self.assertTrue('does not exist' in str(e))
    
    def testLazyAttributeSequence(self):
        class TestObjectFactory(Factory):
            one = LazyAttributeSequence(lambda a, n: 'abc' + n)
            two = LazyAttributeSequence(lambda a, n: a.one + ' xyz' + n)
            
        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'abc0')
        self.assertEqual(test_object0.two, 'abc0 xyz0')
        
        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'abc1')
        self.assertEqual(test_object1.two, 'abc1 xyz1')
        
    def testLazyAttributeDecorator(self):
        class TestObjectFactory(Factory):
            @lazy_attribute
            def one(a):
                return 'one'
                
        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')
        
    def testSequenceDecorator(self):
        class TestObjectFactory(Factory):
            @sequence
            def one(n):
                return 'one' + n
                
        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')
        
    def testLazyAttributeSequenceDecorator(self):
        class TestObjectFactory(Factory):
            @lazy_attribute_sequence
            def one(a, n):
                return 'one' + n
            @lazy_attribute_sequence
            def two(a, n):
                return a.one + ' two' + n
                  
        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')
        self.assertEqual(test_object.two, 'one0 two0')
    
    def testBuildWithParameters(self):
        class TestObjectFactory(Factory):
            one = Sequence(lambda n: 'one' + n)
            two = Sequence(lambda n: 'two' + n)
            
        test_object0 = TestObjectFactory.build(three='three')
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')
        self.assertEqual(test_object0.three, 'three')
        
        test_object1 = TestObjectFactory.build(one='other')
        self.assertEqual(test_object1.one, 'other')
        self.assertEqual(test_object1.two, 'two1')
        
    def testCreate(self):
        class TestModelFactory(Factory):
            one = 'one'
        
        test_model = TestModelFactory.create()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)
        
    def testInheritance(self):
        class TestObjectFactory(Factory):
            one = 'one'
            two = LazyAttribute(lambda a: a.one + ' two')
                    
        class TestObjectFactory2(TestObjectFactory):
            FACTORY_FOR = TestObject
            
            three = 'three'
            four = LazyAttribute(lambda a: a.three + ' four')
            
        test_object = TestObjectFactory2.build()
        self.assertEqual(test_object.one, 'one')
        self.assertEqual(test_object.two, 'one two')
        self.assertEqual(test_object.three, 'three')
        self.assertEqual(test_object.four, 'three four')
            
    def testInheritanceWithInheritedClass(self):
        class TestObjectFactory(Factory):
            one = 'one'
            two = LazyAttribute(lambda a: a.one + ' two')
                
        class TestFactory(TestObjectFactory):
            three = 'three'
            four = LazyAttribute(lambda a: a.three + ' four')
        
        test_object = TestFactory.build()
        self.assertEqual(test_object.one, 'one')
        self.assertEqual(test_object.two, 'one two')
        self.assertEqual(test_object.three, 'three')
        self.assertEqual(test_object.four, 'three four')
    
    def testSetCreationFunction(self):
        def creation_function(class_to_create, **kwargs):
            return "This doesn't even return an instance of {0}".format(class_to_create.__name__)
            
        class TestModelFactory(Factory):
            pass
            
        TestModelFactory.set_creation_function(creation_function)
        
        test_object = TestModelFactory.create()
        self.assertEqual(test_object, "This doesn't even return an instance of TestModel")

class FactoryDefaultStrategyTestCase(unittest.TestCase):
    def setUp(self):
        self.default_strategy = Factory.default_strategy
        
    def tearDown(self):
        Factory.default_strategy = self.default_strategy
           
    def testBuildStrategy(self):
        Factory.default_strategy = BUILD_STRATEGY
        
        class TestModelFactory(Factory):
            one = 'one'
            
        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)
        
    def testCreateStrategy(self):
        # Default default_strategy
        
        class TestModelFactory(Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)
        
    def testStubStrategy(self):
        Factory.default_strategy = STUB_STRATEGY
        
        class TestModelFactory(Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(hasattr(test_model, 'id'))  # We should have a plain old object
        
    def testUnknownStrategy(self):
        Factory.default_strategy = 'unknown'
        
        class TestModelFactory(Factory):
            one = 'one'

        self.assertRaises(Factory.UnknownStrategy, TestModelFactory)
        
    def testStubWithNonStubStrategy(self):        
        class TestModelFactory(StubFactory):
            one = 'one'
            
        TestModelFactory.default_strategy = CREATE_STRATEGY

        self.assertRaises(StubFactory.UnsupportedStrategy, TestModelFactory)

class FactoryCreationTestCase(unittest.TestCase):
    def testFactoryFor(self):
        class TestFactory(Factory):
            FACTORY_FOR = TestObject
               
        self.assertTrue(isinstance(TestFactory.build(), TestObject))
        
    def testAutomaticAssociatedClassDiscovery(self):
        class TestObjectFactory(Factory):
            pass
            
        self.assertTrue(isinstance(TestObjectFactory.build(), TestObject))
    
    def testStub(self):
        class TestFactory(StubFactory):
            pass
            
        self.assertEqual(TestFactory.default_strategy, STUB_STRATEGY)
    
    def testInheritanceWithStub(self):
        class TestObjectFactory(StubFactory):
            pass

        class TestFactory(TestObjectFactory):
            pass

        self.assertEqual(TestFactory.default_strategy, STUB_STRATEGY)
    
    # Errors
    
    def testNoAssociatedClassWithAutodiscovery(self):
        try:
            class TestFactory(Factory):
                pass
            self.fail()
        except Factory.AssociatedClassError as e:
            self.assertTrue('autodiscovery' in str(e))
            
    def testNoAssociatedClassWithoutAutodiscovery(self):
        try:
            class Test(Factory):
                pass
            self.fail()
        except Factory.AssociatedClassError as e:
            self.assertTrue('autodiscovery' not in str(e))
            
    def testInheritanceWithConflictingClassesError(self):
        class TestObjectFactory(Factory):
            pass

        try:
            class TestModelFactory(TestObjectFactory):
                pass
            self.fail()
        except Factory.AssociatedClassError as e:
            self.assertTrue('conflicting' in str(e))
            
    def testInheritanceFromMoreThanOneFactory(self):
        class TestObjectFactory(StubFactory):
            pass

        class TestModelFactory(TestObjectFactory):
            pass

        try:
            class TestFactory(TestObjectFactory, TestModelFactory):
                pass
            self.fail()
        except RuntimeError as e:
            self.assertTrue('one Factory' in str(e))

if __name__ == '__main__':
    unittest.main()