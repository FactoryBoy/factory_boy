from django.test import TestCase

from .factories import CustomerRideFactory


class RelatedPostGenerationTest(TestCase):
    def test_usage(self):
        ride = CustomerRideFactory()

