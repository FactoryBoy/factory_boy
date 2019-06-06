from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from .factories import GroupFactory, TaggedGroupFactory, TaggedUserFactory, UserFactory


class GenericFactoryTest(TestCase):

    def test_user_factory(self):
        user = UserFactory()
        self.assertEqual(user.first_name, 'Adam')

    def test_group_factory(self):
        group = GroupFactory()
        self.assertEqual(group.name, 'group')

    def test_generic_user(self):
        model = TaggedUserFactory(tag='user')
        self.assertEqual(model.tag, 'user')
        self.assertTrue(isinstance(model.content_object, User))
        self.assertEqual(model.content_type, ContentType.objects.get_for_model(model.content_object))

    def test_generic_group(self):
        model = TaggedGroupFactory(tag='group')
        self.assertEqual(model.tag, 'group')
        self.assertTrue(isinstance(model.content_object, Group))
        self.assertEqual(model.content_type, ContentType.objects.get_for_model(model.content_object))
